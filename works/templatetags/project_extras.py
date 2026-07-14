import re
from urllib.parse import urlparse

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

from works.media_utils import media_file_url

register = template.Library()

_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
_BOLD_PATTERN = re.compile(r'\*\*(.+?)\*\*')
_ITALIC_PATTERN = re.compile(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)')
_LIST_ITEM_PATTERN = re.compile(r'^[-*]\s+(.+)$')


def _safe_href(url):
    parsed = urlparse(url.strip())
    if parsed.scheme in {'http', 'https'} and parsed.netloc:
        return escape(parsed.geturl())
    return ''


def _inline_markdown(text):
    safe_text = escape(text)

    def link_replacer(match):
        label = match.group(1)
        href = _safe_href(match.group(2))
        if not href:
            return escape(label)
        return (
            f'<a href="{href}" rel="noopener noreferrer" '
            f'class="text-[#f5c518] underline decoration-[#f5c518]/35 '
            f'underline-offset-4 transition-colors hover:text-white">'
            f'{escape(label)}</a>'
        )

    safe_text = _LINK_PATTERN.sub(link_replacer, safe_text)
    safe_text = _BOLD_PATTERN.sub(r'<strong class="font-normal text-white/90">\1</strong>', safe_text)
    safe_text = _ITALIC_PATTERN.sub(r'<em>\1</em>', safe_text)
    return safe_text


@register.filter
def media_url(file_field):
    return media_file_url(file_field)


@register.filter
def project_markdown(value):
    if not value:
        return ''

    blocks = []
    paragraph_lines = []
    list_items = []

    def flush_paragraph():
        nonlocal paragraph_lines
        if not paragraph_lines:
            return
        content = '<br>'.join(_inline_markdown(line) for line in paragraph_lines)
        blocks.append(
            f'<p class="font-light leading-relaxed text-white/75">{content}</p>'
        )
        paragraph_lines = []

    def flush_list():
        nonlocal list_items
        if not list_items:
            return
        items = ''.join(
            f'<li class="font-light leading-relaxed text-white/75">{_inline_markdown(item)}</li>'
            for item in list_items
        )
        blocks.append(f'<ul class="project-markdown-list space-y-2 pl-5">{items}</ul>')
        list_items = []

    for raw_line in str(value).strip().splitlines():
        line = raw_line.strip()
        if not line:
            flush_paragraph()
            flush_list()
            continue

        list_match = _LIST_ITEM_PATTERN.match(line)
        if list_match:
            flush_paragraph()
            list_items.append(list_match.group(1))
            continue

        flush_list()
        paragraph_lines.append(line)

    flush_paragraph()
    flush_list()
    return mark_safe(''.join(blocks))
