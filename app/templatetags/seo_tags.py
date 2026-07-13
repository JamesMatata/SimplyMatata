from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def absolute_uri(context, url=''):
    if not url:
        return ''
    if url.startswith(('http://', 'https://')):
        return url
    request = context.get('request')
    if not request:
        return url
    return request.build_absolute_uri(url)
