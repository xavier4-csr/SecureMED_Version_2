import os
from dotenv import load_dotenv
load_dotenv()


def _get_redis_url():
    """Return the Redis URL from env, or None if not configured."""
    url = os.environ.get("REDIS_URL", "").strip()
    return url if url else None


class Config:
    SECRET_KEY              = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    # Keep the public app on fabricated data until the production access model
    # and managed key handling have been independently reviewed.
    DEMO_MODE               = True

    # ── Session storage ──────────────────────────────────────────────
    # Use Redis if available (Render paid tier), otherwise fall back to
    # filesystem-based sessions (works on free tier without Redis).
    REDIS_URL               = _get_redis_url()
    if REDIS_URL:
        import redis
        SESSION_TYPE        = "redis"
        SESSION_REDIS       = redis.from_url(REDIS_URL)
        RATELIMIT_STORAGE_URI = REDIS_URL
    else:
        SESSION_TYPE        = "filesystem"
        RATELIMIT_STORAGE_URI = "memory://"

    SESSION_PERMANENT       = False
    SESSION_USE_SIGNER      = True
    SESSION_KEY_PREFIX      = "securemed:"
    RATELIMIT_STRATEGY      = "fixed-window"

    # ── Cookie security ──────────────────────────────────────────────
    # Secure cookies only in production (when RENDER env var is set).
    SESSION_COOKIE_SECURE   = os.environ.get("RENDER") is not None
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    PBKDF2_ITERATIONS       = 600_000
    OTP_WINDOW              = 1

    # ── LAN / mobile access ──────────────────────────────────────────
    BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
