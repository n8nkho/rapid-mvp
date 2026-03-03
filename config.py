"""
Application configuration with startup validation.
Fail fast if required environment variables are missing.
"""
import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# Required for normal operation
REQUIRED_ENV = ["SUPABASE_URL", "SUPABASE_KEY"]
# Optional; LLM features degrade without ANTHROPIC_API_KEY
# When API_KEY is set, all non-public routes require X-API-Key or Authorization: Bearer <key>
OPTIONAL_ENV = ["ANTHROPIC_API_KEY", "DATABASE_URL", "CORS_ORIGINS", "ADMIN_API_KEY", "API_KEY"]


def _get_cors_origins() -> List[str]:
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    return [
        "https://rapid-ui-wine.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


def validate_config() -> None:
    """Validate required env vars. Call at application startup."""
    missing = [k for k in REQUIRED_ENV if not os.getenv(k)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Set them or copy .env.example to .env and fill in values."
        )
    for k in OPTIONAL_ENV:
        if not os.getenv(k) and k == "ANTHROPIC_API_KEY":
            logger.warning("ANTHROPIC_API_KEY not set; LLM-based features will fail.")
    logger.info("Config validated successfully.")


def get_cors_origins() -> List[str]:
    return _get_cors_origins()


def get_api_key() -> Optional[str]:
    """Return API key if set; when set, protected routes require X-API-Key or Authorization: Bearer."""
    return os.getenv("API_KEY") or None
