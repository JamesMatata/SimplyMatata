"""Helpers for optional project content stored in the details JSON field."""


def normalize_details(value):
    """Return a safe dict for details, never raising on bad stored data."""
    if value in (None, '', {}):
        return {}
    if not isinstance(value, dict):
        return {}

    normalized = {}

    for key in ('overview', 'description', 'additional'):
        raw = value.get(key)
        if isinstance(raw, str) and raw.strip():
            normalized[key] = raw.strip()

    highlights = value.get('highlights')
    if isinstance(highlights, list):
        cleaned_highlights = []
        for item in highlights:
            if not isinstance(item, dict):
                continue
            label = str(item.get('label', '')).strip()
            body = str(item.get('value') or item.get('body') or '').strip()
            if label and body:
                cleaned_highlights.append({'label': label, 'value': body})
        if cleaned_highlights:
            normalized['highlights'] = cleaned_highlights

    tools = value.get('tools')
    if isinstance(tools, str) and tools.strip():
        normalized['tools'] = [part.strip() for part in tools.split(',') if part.strip()]
    elif isinstance(tools, list):
        cleaned_tools = [str(item).strip() for item in tools if str(item).strip()]
        if cleaned_tools:
            normalized['tools'] = cleaned_tools

    meta = value.get('meta')
    if isinstance(meta, dict):
        cleaned_meta = {}
        for key in ('year', 'role', 'client'):
            raw = meta.get(key)
            if raw is not None and str(raw).strip():
                cleaned_meta[key] = str(raw).strip()
        if cleaned_meta:
            normalized['meta'] = cleaned_meta

    return normalized


def build_details_from_form(cleaned_data):
    """Build details JSON from optional admin form fields."""
    details = {}

    overview = (cleaned_data.get('overview') or '').strip()
    if overview:
        details['overview'] = overview

    additional = (cleaned_data.get('additional') or '').strip()
    if additional:
        details['additional'] = additional

    tools_raw = (cleaned_data.get('tools') or '').strip()
    if tools_raw:
        details['tools'] = [
            part.strip()
            for part in tools_raw.split(',')
            if part.strip()
        ]

    meta = {}
    for key, field in (
        ('year', 'meta_year'),
        ('role', 'meta_role'),
        ('client', 'meta_client'),
    ):
        value = (cleaned_data.get(field) or '').strip()
        if value:
            meta[key] = value
    if meta:
        details['meta'] = meta

    return details


DETAILS_GUIDE = (
    'All fields below are optional. Leave them blank if you only need title, tagline, and media.\n\n'
    'Overview — long-form description shown on the project page.\n'
    'Additional notes — extra context below the overview.\n'
    'Tools — comma-separated list for software projects (e.g. Django, PostgreSQL).\n'
    'Year / Role / Client — small metadata shown in the project header.'
)

DETAILS_EXAMPLE = (
    '{\n'
    '  "overview": "Short description of the work.",\n'
    '  "meta": {"year": "2025", "role": "Director"}\n'
    '}'
)
