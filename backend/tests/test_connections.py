import uuid

def test_material_connections_and_backlinks(client):
    # 1. Registrar um usuário isolado para o teste
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "StrongPassword123!"
    reg_res = client.post("/api/auth/register", json={"name": "Grafo Test", "email": email, "password": pwd})
    assert reg_res.status_code == 201, reg_res.text

    # Login
    login_res = client.post("/api/auth/login", json={"email": email, "password": pwd})
    assert login_res.status_code == 200

    # 2. Criar 2 materiais via upload simulado
    # Material A: Redes de Computadores
    pdf_content = b"%PDF-1.4 1 0 obj << /Type /Catalog >> endobj xref 0 1 trailer << /Root 1 0 R >> %%EOF"
    res_a = client.post(
        "/api/materials",
        data={"title": "Redes de Computadores"},
        files={"file": ("redes.pdf", pdf_content, "application/pdf")},
    )
    assert res_a.status_code == 201, res_a.text
    mat_a_id = res_a.json()["id"]

    # Material B: Segurança da Informação
    res_b = client.post(
        "/api/materials",
        data={"title": "Segurança da Informação"},
        files={"file": ("seguranca.pdf", pdf_content, "application/pdf")},
    )
    assert res_b.status_code == 201, res_b.text
    mat_b_id = res_b.json()["id"]

    # 3. Conectar: Segurança -> Redes como pré-requisito
    conn_res = client.post(
        f"/api/materials/{mat_b_id}/connections",
        json={
            "target_material_id": mat_a_id,
            "relation_type": "prerequisite",
            "note": "Necessário entender TCP/IP antes de estudar firewalls",
        },
    )
    assert conn_res.status_code == 201, conn_res.text
    conn_data = conn_res.json()
    assert conn_data["source_material_id"] == mat_b_id
    assert conn_data["target_material_id"] == mat_a_id
    assert conn_data["relation_type"] == "prerequisite"
    conn_id = conn_data["id"]

    # 4. Verificar listagem a partir de Segurança (deve constar em outgoing)
    res_conns_b = client.get(f"/api/materials/{mat_b_id}/connections")
    assert res_conns_b.status_code == 200
    b_data = res_conns_b.json()
    assert len(b_data["outgoing"]) == 1
    assert b_data["outgoing"][0]["target_material_id"] == mat_a_id
    assert b_data["outgoing"][0]["target_material_title"] == "Redes de Computadores"
    assert len(b_data["incoming"]) == 0

    # 5. Verificar backlinks em Redes (deve constar em incoming)
    res_conns_a = client.get(f"/api/materials/{mat_a_id}/connections")
    assert res_conns_a.status_code == 200
    a_data = res_conns_a.json()
    assert len(a_data["outgoing"]) == 0
    assert len(a_data["incoming"]) == 1
    assert a_data["incoming"][0]["source_material_id"] == mat_b_id
    assert a_data["incoming"][0]["source_material_title"] == "Segurança da Informação"
    assert a_data["incoming"][0]["note"] == "Necessário entender TCP/IP antes de estudar firewalls"

    # 6. Remover conexão e verificar remoção mútua
    del_res = client.delete(f"/api/connections/{conn_id}")
    assert del_res.status_code == 204

    # Checar que agora ambos estão sem links
    after_b = client.get(f"/api/materials/{mat_b_id}/connections").json()
    assert len(after_b["outgoing"]) == 0
    after_a = client.get(f"/api/materials/{mat_a_id}/connections").json()
    assert len(after_a["incoming"]) == 0
