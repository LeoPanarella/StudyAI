import uuid
from datetime import datetime, timezone
from app.db.session import SessionLocal
from app.models.flashcard import Flashcard
from app.models.material import Material
from app.models.user import User


def test_sm2_algorithm_calculations(client):
    # 1. Registrar e autenticar usuário
    email = f"sm2_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "StrongPassword123!"
    client.post("/api/auth/register", json={"name": "SM2 User", "email": email, "password": pwd})
    client.post("/api/auth/login", json={"email": email, "password": pwd})

    # 2. Criar material e flashcard inicial no banco
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()
        mat = Material(
            user_id=user.id,
            title="Material SM2",
            filename="teste.pdf",
            stored_path="/tmp/fake.pdf",
            file_size=100,
            page_count=1,
            content_text="Texto de teste",
            char_count=14,
        )
        db.add(mat)
        db.commit()
        db.refresh(mat)

        card = Flashcard(
            material_id=mat.id,
            question="Qual a fórmula da água?",
            answer="H2O",
            repetitions=0,
            interval_days=0,
            ease_factor=2.5,
        )
        db.add(card)
        db.commit()
        db.refresh(card)
        card_id = card.id

    # 3. Teste Rating 2 (Bom / Good) no primeiro estudo -> intervalo deve ir para 1 dia
    res1 = client.post(f"/api/flashcards/{card_id}/review", json={"rating": 2})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["repetitions"] == 1
    assert data1["interval_days"] == 1
    # EF para rating 2: EF' = 2.5 + (0.1 - (3-2)*(0.08 + (3-2)*0.02)) = 2.5 + (0.1 - 0.10) = 2.5
    assert abs(data1["ease_factor"] - 2.5) < 0.01

    # 4. Teste Rating 3 (Fácil / Easy) no segundo estudo -> intervalo deve ir para 6 dias
    res2 = client.post(f"/api/flashcards/{card_id}/review", json={"rating": 3})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["repetitions"] == 2
    assert data2["interval_days"] == 6
    # EF para rating 3 deve subir para 2.6
    assert abs(data2["ease_factor"] - 2.6) < 0.01

    # 5. Teste Rating 0 (Errei / Again) -> repetições zeram, intervalo volta a 1 dia
    res3 = client.post(f"/api/flashcards/{card_id}/review", json={"rating": 0})
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["repetitions"] == 0
    assert data3["interval_days"] == 1
    # EF com q=1: 2.6 + (0.1 - 4 * (0.08 + 4 * 0.02)) = 2.6 - 0.54 = 2.06
    assert abs(data3["ease_factor"] - 2.06) < 0.01

    # 6. Teste de piso mínimo do Ease Factor (não pode cair abaixo de 1.3)
    with SessionLocal() as db:
        c = db.get(Flashcard, card_id)
        c.ease_factor = 1.35
        db.commit()

    res4 = client.post(f"/api/flashcards/{card_id}/review", json={"rating": 0})
    assert res4.status_code == 200
    data4 = res4.json()
    assert data4["ease_factor"] >= 1.3
