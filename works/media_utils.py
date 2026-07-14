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


def youtube_video_id(url):
    """Extract a YouTube video ID from common URL formats."""
    value = (url or '').strip()
    if not value:
        return ''
    if '/embed/' in value:
        return value.rsplit('/embed/', 1)[-1].split('?')[0]
    if 'youtu.be/' in value:
        return value.rsplit('youtu.be/', 1)[-1].split('?')[0]
    if '/shorts/' in value:
        return value.rsplit('/shorts/', 1)[-1].split('?')[0]
    if 'v=' in value:
        return value.split('v=', 1)[-1].split('&')[0]
    return ''


def youtube_embed_url(url, autoplay=False, controls=True, allow_fullscreen=True):
    """Build a privacy-enhanced YouTube embed URL."""
    video_id = youtube_video_id(url)
    if not video_id:
        return ''
    params = ['rel=0', 'modestbranding=1', 'playsinline=1']
    if autoplay:
        params.extend(['autoplay=1', 'mute=1'])
    if not controls:
        params.append('controls=0')
    # Disable YouTube's own fullscreen so it does not fight our modal player state.
    if not allow_fullscreen:
        params.append('fs=0')
    return f'https://www.youtube-nocookie.com/embed/{video_id}?{"&".join(params)}'
