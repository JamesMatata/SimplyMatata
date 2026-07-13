from datetime import timedelta

from django.db.models import Count, Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import AnonymousCommentForm
from .models import AnonymousComment, ComicPage, Project, SeriesEpisode
from .utils import get_client_ip

RATE_LIMIT = 3
RATE_WINDOW = timedelta(hours=1)


def is_rate_limited(ip_address):
    if not ip_address:
        return False
    cutoff = timezone.now() - RATE_WINDOW
    return AnonymousComment.objects.filter(
        ip_address=ip_address,
        created_at__gte=cutoff,
    ).count() >= RATE_LIMIT


def _comic_pages_payload(pages):
    return [
        {
            'number': page.page_number,
            'image': page.image.url,
        }
        for page in pages
    ]


def _series_episodes_payload(episodes):
    payload = []
    for episode in episodes:
        item = {
            'number': episode.number,
            'title': episode.title,
            'tagline': episode.tagline,
            'cover': episode.card_thumbnail.url,
            'page_count': episode.comic_page_count,
            'has_video': episode.has_featured_video,
        }
        if episode.project.is_comic:
            item['pages'] = _comic_pages_payload(episode.comic_pages.all())
        payload.append(item)
    return payload


def _published_projects_queryset():
    return (
        Project.objects.filter(is_published=True)
        .prefetch_related('media')
        .annotate(_episode_count=Count('episodes', distinct=True))
    )


def works_list(request):
    projects = list(_published_projects_queryset())
    return render(request, 'works.html', {
        'projects': projects,
        'total_count': len(projects),
        'software_count': sum(1 for p in projects if p.track == 'software'),
        'storytelling_count': sum(1 for p in projects if p.track == 'storytelling'),
        'page_title': 'Works — James Matata',
        'meta_description': (
            'Browse the full archive of software, film, comic, '
            'and advertising projects by James Matata.'
        ),
    })


def project_detail(request, slug):
    episodes_prefetch = Prefetch(
        'episodes',
        queryset=SeriesEpisode.objects.prefetch_related(
            Prefetch('comic_pages', queryset=ComicPage.objects.order_by('page_number')),
            'media',
        ).order_by('number'),
    )
    project = get_object_or_404(
        Project.objects.prefetch_related(
            'media',
            Prefetch('comic_pages', queryset=ComicPage.objects.order_by('page_number')),
            episodes_prefetch,
        ).annotate(_episode_count=Count('episodes', distinct=True)),
        slug=slug,
        is_published=True,
    )
    comic_pages = _comic_pages_payload(project.comic_pages.all())
    series_episodes = _series_episodes_payload(project.episodes.all()) if project.show_episodes else []

    seo_description = project.tagline.strip()
    if not seo_description and project.overview:
        seo_description = project.overview.strip()[:300]

    seo_og_image = ''
    if project.featured_image:
        seo_og_image = request.build_absolute_uri(project.featured_image.url)

    return render(request, 'project_detail.html', {
        'project': project,
        'comic_pages': comic_pages,
        'series_episodes': series_episodes,
        'page_title': f'{project.title} — James Matata',
        'meta_description': seo_description,
        'seo_og_image': seo_og_image,
        'og_image_alt': f'{project.title} — {project.tagline}',
        'og_type': 'article',
    })


@require_POST
def post_comment(request, slug):
    project = get_object_or_404(Project, slug=slug, is_published=True)
    form = AnonymousCommentForm(request.POST)

    if form.honeypot_triggered:
        return JsonResponse({
            'status': 'success',
            'comment': '',
            'timestamp': timezone.now().isoformat(),
        })

    if not form.is_valid():
        content_errors = form.errors.get('content')
        message = content_errors[0] if content_errors else 'Please check your note and try again.'
        return JsonResponse({
            'status': 'error',
            'message': message,
            'errors': form.errors.get_json_data(),
        }, status=400)

    ip_address = get_client_ip(request)

    if is_rate_limited(ip_address):
        return JsonResponse({
            'status': 'error',
            'message': 'Rate limit exceeded. Please try again later.',
        }, status=429)

    comment = AnonymousComment.objects.create(
        project=project,
        content=form.cleaned_data['content'],
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:512],
    )

    return JsonResponse({
        'status': 'success',
        'comment': comment.content,
        'timestamp': comment.created_at.isoformat(),
    })
