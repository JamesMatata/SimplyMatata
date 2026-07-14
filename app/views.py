from django.db.models import Count
from django.shortcuts import render

from works.models import Project


def index(request):
    featured_projects = (
        Project.objects.filter(is_published=True, homepage_slot__isnull=False)
        .prefetch_related('media')
        .annotate(_episode_count=Count('episodes', distinct=True))
        .order_by('homepage_slot')[:3]
    )
    return render(request, 'index.html', {
        'featured_projects': featured_projects,
        'page_title': 'James Matata — Portfolio',
        'meta_description': (
            'James Matata — software architect and story director. '
            'Explore software systems, films, comics, and advertising projects.'
        ),
    })


def about(request):
    return render(request, 'about.html', {
        'page_title': 'About — James Matata',
        'meta_description': (
            'About James Matata — background, creative approach, '
            'and the story behind SimplyMatata.'
        ),
    })


def contact(request):
    return render(request, 'contact.html', {
        'page_title': 'Contact — James Matata',
        'meta_description': (
            'Get in touch with James Matata for collaborations, '
            'commissions, and project inquiries.'
        ),
    })
