import ipaddress

from django.conf import settings


def get_client_ip(request) -> str | None:
    """
    Resolve the client IP for rate limiting and auditing.

    Only trusts X-Forwarded-For when the app runs behind a known reverse proxy.
    Otherwise uses REMOTE_ADDR so clients cannot spoof their IP.
    """
    remote_addr = (request.META.get('REMOTE_ADDR') or '').strip()

    if getattr(settings, 'USE_TRUSTED_PROXY', False):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded:
            candidate = forwarded.split(',')[0].strip()
            if _is_valid_ip(candidate):
                return candidate

    if remote_addr and _is_valid_ip(remote_addr):
        return remote_addr

    return None


def _is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return False
    return True
