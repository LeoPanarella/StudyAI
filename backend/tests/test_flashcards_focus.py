import uuid
from app.services.ai.flashcards_generator import score_chunk_focus

def test_chunk_scoring_by_focus_keywords():
    chunk1 = "O modelo OSI possui 7 camadas, sendo a camada física a mais baixa e a de aplicação a mais alta."
    chunk2 = "A fotossíntese converte energia luminosa em energia química armazenada em moléculas de glicose."
    chunk3 = "O protocolo TCP garante entrega confiável com handshake em três vias (SYN, SYN-ACK, ACK)."

    focus = "camadas modelo OSI e protocolo TCP"
    score1 = score_chunk_focus(chunk1, focus)
    score2 = score_chunk_focus(chunk2, focus)
    score3 = score_chunk_focus(chunk3, focus)

    assert score1 > 0
    assert score3 > 0
    assert score2 == 0
    assert score1 > score2

def test_flashcard_generation_request_with_focus(client):
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "StrongPassword123!"
    client.post("/api/auth/register", json={"name": "Focus User", "email": email, "password": pwd})
    client.post("/api/auth/login", json={"email": email, "password": pwd})

    # Criar material com texto
    pdf_content = b"%PDF-1.4 1 0 obj << /Type /Catalog >> endobj xref 0 1 trailer << /Root 1 0 R >> %%EOF"
    res = client.post(
        "/api/materials",
        data={"title": "Redes de Computadores Completo"},
        files={"file": ("redes.pdf", pdf_content, "application/pdf")},
    )
    mat_id = res.json()["id"]

    # Simular texto extraído diretamente no DB para possibilitar geração de flashcards
    from app.db.session import SessionLocal
    from app.models.material import Material
    with SessionLocal() as db:
        m = db.get(Material, mat_id)
        m.content_text = "Capítulo 1: Introdução ao modelo OSI de 7 camadas. Camada 1 Física, Camada 2 Enlace, Camada 3 Rede, Camada 4 Transporte. Capítulo 2: Segurança com criptografia assimétrica RSA e curvas elípticas."
        m.char_count = len(m.content_text)
        db.commit()

    # Requisitar geração de flashcards focados no modelo OSI
    gen_res = client.post(
        f"/api/materials/{mat_id}/flashcards/generate",
        json={"focus": "modelo OSI e 7 camadas"},
    )
    assert gen_res.status_code == 202, gen_res.text
    job_data = gen_res.json()
    assert job_data["kind"] == "flashcards"
    assert job_data["focus"] == "modelo OSI e 7 camadas"
