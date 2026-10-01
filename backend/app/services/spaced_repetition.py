"""Implementação do algoritmo SM-2 (SuperMemo 2) de repetição espaçada.

Adaptado para escala de 4 avaliações intuitivas:
- 0: Errei (Again) -> repete em 1 dia, zera repetições
- 1: Difícil (Hard) -> avanço conservador
- 2: Bom (Good) -> intervalo ideal calculado pelo ease_factor
- 3: Fácil (Easy) -> avanço acelerado com bônus de intervalo
"""

from datetime import datetime, timedelta, timezone


def apply_sm2(
    repetitions: int,
    interval_days: int,
    ease_factor: float,
    rating: int,  # 0..3
) -> tuple[int, int, float, datetime, datetime]:
    """Calcula os novos valores SM-2 após uma revisão.

    Retorna: (new_repetitions, new_interval_days, new_ease_factor, next_review_at, last_reviewed_at)
    """
    now = datetime.now(timezone.utc)

    # Mapeia rating (0..3) para qualidade SuperMemo (1..5)
    quality_map = {
        0: 1,  # Errei
        1: 3,  # Difícil
        2: 4,  # Bom
        3: 5,  # Fácil
    }
    q = quality_map.get(rating, 3)

    # Atualiza Ease Factor (EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
    new_ef = ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    new_ef = max(1.3, min(3.0, round(new_ef, 2)))

    if rating == 0:
        # Errou: reinicia ciclo de memorização
        new_reps = 0
        new_interval = 1
    else:
        if repetitions == 0:
            new_interval = 1 if rating <= 2 else 3
        elif repetitions == 1:
            new_interval = 3 if rating <= 2 else 6
        else:
            multiplier = 1.3 if rating == 3 else 1.0
            new_interval = max(1, round(interval_days * new_ef * multiplier))
        new_reps = repetitions + 1

    next_review = now + timedelta(days=new_interval)
    return new_reps, new_interval, new_ef, next_review, now
