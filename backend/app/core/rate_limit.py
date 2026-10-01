import time
from collections import defaultdict
from threading import Lock
from fastapi import HTTPException, Request, status
from app.core.config import settings


class InMemoryRateLimiter:
    """Rate limiter em memória baseado em janela deslizante (Sliding Window).
    
    Não necessita de Redis para implantações simples/médias e protege rotas
    sensíveis contra abuso, brute-force e exaustão de cotas de IA.
    """
    def __init__(self, requests_limit: int, window_seconds: int):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.records = defaultdict(list)
        self.lock = Lock()

    def __call__(self, request: Request):
        # Chave baseada no IP real do cliente (considerando proxies reversos)
        forwarded = request.headers.get("x-forwarded-for")
        client_ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")
        key = f"{client_ip}:{request.url.path}"
        now = time.time()

        # Em desenvolvimento, desativa restrição para não bloquear testes e apresentações
        if settings.ENV == "development":
            return
            # Filtra registros fora da janela atual
            timestamps = [t for t in self.records[key] if now - t < self.window_seconds]
            if len(timestamps) >= self.requests_limit:
                retry_after = int(self.window_seconds - (now - timestamps[0])) + 1
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Limite de requisições excedido. Tente novamente em {retry_after} segundos.",
                    headers={"Retry-After": str(retry_after)},
                )
            timestamps.append(now)
            self.records[key] = timestamps


# Limitadores reutilizáveis
login_limiter = InMemoryRateLimiter(requests_limit=10, window_seconds=60)
ai_generation_limiter = InMemoryRateLimiter(requests_limit=6, window_seconds=60)
