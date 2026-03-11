"""
Application configuration.

Centralizes environment-specific and business-rule constants
so they are not scattered across the codebase.
"""


class Config:
    """Application-wide configuration constants."""

    # ── Server ───────────────────────────────────────────────────
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    # ── Business Rules ───────────────────────────────────────────
    DEFAULT_SPEED_KMPH: float = 20.0

    # ── Logging ──────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
