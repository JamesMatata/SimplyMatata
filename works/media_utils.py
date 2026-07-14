def media_file_url(file_field):
    """Return a file URL or empty string; never raise on missing files."""
    if not file_field:
        return ''
    try:
        name = getattr(file_field, 'name', '') or ''
        if not name:
            return ''
        return file_field.url
    except (ValueError, OSError, AttributeError):
        return ''
