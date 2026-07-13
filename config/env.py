import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


def load_env_file(base_dir: Path) -> None:
    """Load variables from .env when python-dotenv is installed."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    load_dotenv(base_dir / '.env')


def env_bool(name: str, *, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def env_list(name: str, *, default: list[str] | None = None) -> list[str]:
    value = os.environ.get(name)
    if value is None:
        return list(default or [])
    return [item.strip() for item in value.split(',') if item.strip()]


def env_int(name: str, *, default: int) -> int:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return default
    return int(value)


def env_str(name: str, *, default: str = '') -> str:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip()


def require_secret_key(*, debug: bool) -> str:
    secret_key = os.environ.get('SECRET_KEY', '').strip()
    if secret_key:
        return secret_key

    if debug:
        return 'django-insecure-dev-only-change-before-production'

    raise ImproperlyConfigured(
        'SECRET_KEY environment variable is required when DEBUG is False.'
    )
