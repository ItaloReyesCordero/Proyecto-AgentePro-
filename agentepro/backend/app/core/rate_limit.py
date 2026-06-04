from __future__ import annotations

import time
from collections import defaultdict

# ---------------------------------------------------------------------------
# Limitador de ventana fija, en memoria del proceso.
#
# Lo usa `RateLimitMiddleware` como FALLBACK cuando Redis no está disponible,
# para no quedar "fail-open" (sin protección) en las rutas sensibles de auth.
# Nota: en multi-worker el conteo es POR worker; el límite global exacto lo da
# Redis. La lógica se aísla aquí para poder probarla sin levantar HTTP.
# ---------------------------------------------------------------------------


class FixedWindowLimiter:
    """Cuenta accesos por clave dentro de ventanas de tiempo fijas."""

    def __init__(self, max_hits: int, window_seconds: int) -> None:
        self.max_hits = max_hits
        self.window = window_seconds
        # clave -> (inicio_de_ventana, conteo)
        self._buckets: dict[str, tuple[float, int]] = defaultdict(lambda: (0.0, 0))

    def allow(self, key: str, now: float | None = None) -> bool:
        """Registra un acceso y devuelve True si está permitido, False si excede."""
        now = time.monotonic() if now is None else now
        start, count = self._buckets[key]
        if now - start >= self.window:
            self._buckets[key] = (now, 1)  # ventana nueva
            return True
        if count >= self.max_hits:
            return False
        self._buckets[key] = (start, count + 1)
        return True

    def reset(self) -> None:
        self._buckets.clear()
