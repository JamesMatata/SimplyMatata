from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage


def social_links(request):
    return {
        'social_links': getattr(settings, 'SOCIAL_LINKS', {}),
    }


def site_seo(request):
    default_og_path = staticfiles_storage.url('images/simply-matata-logo.png')
    site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
    if not site_url:
        site_url = request.build_absolute_uri('/').rstrip('/')

    return {
        'site_name': settings.SITE_NAME,
        'site_description': settings.SITE_DESCRIPTION,
        'site_author': settings.SITE_AUTHOR,
        'site_url': site_url,
        'site_default_og_image': request.build_absolute_uri(default_og_path),
    }
