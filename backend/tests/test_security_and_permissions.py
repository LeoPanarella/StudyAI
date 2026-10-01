import uuid

def test_cross_user_isolation(client):
    # Criar Usuário A
    email_a = f"user_a_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "StrongPassword123!"
    client.post("/api/auth/register", json={"name": "User A", "email": email_a, "password": pwd})
    client.post("/api/auth/login", json={"email": email_a, "password": pwd})

    # Usuário A faz upload de PDF válido
    valid_pdf = b"%PDF-1.4 1 0 obj << /Type /Catalog >> endobj xref 0 1 trailer << /Root 1 0 R >> %%EOF"
    res_a = client.post(
        "/api/materials",
        data={"title": "Material Secreto do User A"},
        files={"file": ("secreto.pdf", valid_pdf, "application/pdf")},
    )
    assert res_a.status_code == 201
    mat_a_id = res_a.json()["id"]

    # Criar Usuário B
    email_b = f"user_b_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={"name": "User B", "email": email_b, "password": pwd})
    client.post("/api/auth/login", json={"email": email_b, "password": pwd})

    # Usuário B tenta acessar material do Usuário A -> deve retornar 404 (sem vazar existência)
    get_res = client.get(f"/api/materials/{mat_a_id}")
    assert get_res.status_code == 404

    # Usuário B tenta deletar material do Usuário A -> deve retornar 404
    del_res = client.delete(f"/api/materials/{mat_a_id}")
    assert del_res.status_code == 404

    # Material do Usuário A não deve constar na listagem do Usuário B
    list_b = client.get("/api/materials").json()
    assert all(m["id"] != mat_a_id for m in list_b)


def test_upload_rejection_without_pdf_magic_bytes(client):
    email = f"uploader_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "StrongPassword123!"
    client.post("/api/auth/register", json={"name": "Uploader", "email": email, "password": pwd})
    client.post("/api/auth/login", json={"email": email, "password": pwd})

    # Arquivo de texto comum renomeado para .pdf (sem magic bytes %PDF-)
    fake_pdf = b"Este eh um arquivo de texto comum disfarcado de PDF."
    res = client.post(
        "/api/materials",
        data={"title": "Arquivo Falso"},
        files={"file": ("falso.pdf", fake_pdf, "application/pdf")},
    )
    # Deve rejeitar com 400 Bad Request
    assert res.status_code == 400
    assert "assinatura binária" in res.json()["detail"]


def test_login_rate_limiting(client):
    # Simula tentativas excessivas de login com senha errada
    email = "vitima@exemplo.com"
    for _ in range(10):
        client.post("/api/auth/login", json={"email": email, "password": "wrong-password"})

    # A 11ª requisição no mesmo minuto deve ser bloqueada pelo Rate Limiter (HTTP 429)
    blocked_res = client.post("/api/auth/login", json={"email": email, "password": "wrong-password"})
    assert blocked_res.status_code == 429
    assert "Retry-After" in blocked_res.headers
