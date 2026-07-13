import io
import urllib.request

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from PIL import Image, ImageDraw

from works.models import ComicPage, Project, ProjectMedia, SeriesEpisode


SAMPLE_VIDEOS = [
    'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4',
    'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/friday.mp4',
]

PROJECTS = [
    {
        'title': 'Atlas CMS',
        'category': Project.Category.SOFTWARE,
        'tagline': 'Modular publishing for distributed editorial teams.',
        'overview': (
            'Atlas CMS is a modular editorial platform built for distributed newsrooms. '
            'It separates content modeling, workflow orchestration, and publishing surfaces '
            'so teams can ship faster without sacrificing editorial control.'
        ),
        'highlights': [
            {
                'label': 'Problem',
                'value': (
                    'Distributed editorial teams were juggling disconnected tools for drafting, '
                    'approval, and publishing — slowing releases and creating version drift across channels.'
                ),
            },
            {
                'label': 'Approach',
                'value': (
                    'A modular core with composable content models, role-aware workflows, and '
                    'channel-specific render pipelines. Teams configure only the surfaces they need.'
                ),
            },
            {
                'label': 'Outcome',
                'value': (
                    'Pilot newsrooms reduced publish turnaround by roughly 40% while keeping '
                    'a single source of truth for long-form packages and breaking updates.'
                ),
            },
        ],
        'additional': (
            'Built as an internal platform first, then hardened for multi-tenant editorial partners.\n\n'
            '- Workflow states are configurable per desk\n'
            '- Publishing adapters cover web, newsletter, and syndication feeds'
        ),
        'tools': ['Django', 'PostgreSQL', 'Redis', 'React', 'TypeScript', 'Docker'],
        'meta': {'year': '2025', 'role': 'Lead Engineer'},
        'color': (24, 24, 28),
        'accent': (245, 197, 24),
        'video': False,
        'gallery': [
            {'caption': 'Desk-level workflow board with assignable editorial states.'},
            {'caption': 'Structured content model editor for reusable story packages.'},
            {'caption': 'Multi-channel publish preview before release.'},
        ],
    },
    {
        'title': 'Pulse Energy — Launch',
        'category': Project.Category.ADVERTISING,
        'format': Project.Format.SINGLE,
        'tagline': 'High-energy brand launch for a regional energy drink.',
        'delivery_formats': 'YouTube, TV, Reels',
        'description': (
            'A multi-format launch campaign built for broadcast, pre-roll, and vertical social. '
            'The spot leans on rhythm, product texture, and a single bold payoff.'
        ),
        'meta': {'year': '2025', 'role': 'Director', 'client': 'Pulse Energy'},
        'color': (24, 18, 12),
        'accent': (245, 197, 24),
        'video': True,
        'video_url': SAMPLE_VIDEOS[0],
    },
    {
        'title': 'Midnight Lagos',
        'category': Project.Category.FILM,
        'format': Project.Format.SERIES,
        'tagline': 'A nocturnal anthology tracing transit, light, and memory.',
        'description': (
            'Shot across twelve nights in Lagos, this anthology follows movement through stations, '
            'bridges, and backstreets — each episode treating the city as a living system.'
        ),
        'meta': {'year': '2024', 'role': 'Director'},
        'color': (12, 18, 32),
        'accent': (245, 197, 24),
        'episodes': [
            {
                'title': 'Station Light',
                'tagline': 'Platforms, halos, and the pause before departure.',
                'video_url': SAMPLE_VIDEOS[0],
            },
            {
                'title': 'Bridge Frequency',
                'tagline': 'Crossing points where sound and shadow overlap.',
                'video_url': SAMPLE_VIDEOS[1],
            },
        ],
    },
    {
        'title': 'The Wire Saints',
        'category': Project.Category.COMIC,
        'format': Project.Format.SERIES,
        'tagline': 'Serialized myth-making across twelve illustrated chapters.',
        'description': (
            'The Wire Saints is a twelve-chapter comic series blending street mythology with '
            'speculative technology. Each issue follows a different witness.'
        ),
        'meta': {'year': '2025', 'role': 'Writer / Artist'},
        'color': (28, 16, 20),
        'accent': (245, 197, 24),
        'issues': [
            {
                'title': 'Witness One',
                'tagline': 'The city hums before dawn.',
                'pages': 2,
            },
            {
                'title': 'Signal Corridor',
                'tagline': 'A hallway of light, half memory, half signal.',
                'pages': 2,
            },
            {
                'title': 'Grid Silence',
                'tagline': 'Where the wires go quiet and folklore rewrites itself.',
                'pages': 2,
            },
        ],
    },
    {
        'title': 'Signal Lab 04',
        'category': Project.Category.LAB,
        'tagline': 'Generative motion studies for live visual performance.',
        'description': 'Signal Lab 04 explores real-time motion systems for stage and installation work. The experiments combine procedural animation, audio-reactive shaders, and manual override controls for live direction.',
        'meta': {'year': '2025', 'role': 'Creative Technologist'},
        'color': (18, 22, 26),
        'accent': (245, 197, 24),
        'video': True,
        'video_url': SAMPLE_VIDEOS[1],
    },
    {
        'title': 'Riverframe',
        'category': Project.Category.FILM,
        'tagline': 'Documentary short on craft, water, and inherited rhythm.',
        'description': 'Riverframe documents artisans working along a single river corridor, tracing how technique, family memory, and environment shape what gets made — and what gets left behind.',
        'meta': {'year': '2023', 'role': 'Director / Editor'},
        'color': (16, 28, 30),
        'accent': (245, 197, 24),
        'video': True,
        'video_url': SAMPLE_VIDEOS[0],
    },
    {
        'title': 'Patchwork OS',
        'category': Project.Category.SOFTWARE,
        'tagline': 'Experimental interface kit for narrative product demos.',
        'overview': (
            'Patchwork OS is a design-engineering toolkit for building **narrative product demos**. '
            'It prioritizes motion, typography, and modular scene composition over traditional dashboard patterns.'
        ),
        'highlights': [
            {
                'label': 'Problem',
                'value': (
                    'Product teams needed demo environments that felt cinematic and intentional — '
                    'not like stripped-down admin panels pasted into a pitch deck.'
                ),
            },
            {
                'label': 'Approach',
                'value': (
                    'Scene-based UI primitives, timeline-driven transitions, and a lightweight runtime '
                    'that lets designers assemble flows without rebuilding frontend scaffolding each time.'
                ),
            },
            {
                'label': 'Outcome',
                'value': (
                    'Teams ship polished demo narratives in days instead of weeks, with reusable motion '
                    'patterns that stay consistent across launches.'
                ),
            },
        ],
        'additional': (
            'Patchwork is intentionally opinionated about pacing and typography so demos read as stories, '
            'not feature checklists.\n\n'
            'See the gallery for component snapshots and a motion study from an early prototype pass.'
        ),
        'tools': ['Vue', 'TypeScript', 'Tailwind CSS', 'GSAP', 'Vite', 'Figma'],
        'meta': {'year': '2025', 'role': 'Designer / Developer'},
        'color': (20, 20, 24),
        'accent': (245, 197, 24),
        'video': True,
        'video_url': SAMPLE_VIDEOS[1],
        'gallery': [
            {'caption': 'Scene composer with timeline controls for demo pacing.'},
            {'caption': 'Typography-led hero module used across launch narratives.'},
            {'caption': 'Component sheet for cards, metrics, and story beats.'},
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed published projects with generated posters and main project media.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing seeded projects before creating new ones.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            slugs = [slugify(item['title']) for item in PROJECTS]
            deleted, _ = Project.objects.filter(slug__in=slugs).delete()
            self.stdout.write(self.style.WARNING(f'Removed {deleted} existing seeded records.'))

        created = 0
        for item in PROJECTS:
            slug = slugify(item['title'])
            project, was_created = Project.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': item['title'],
                    'category': item['category'],
                    'format': item.get('format', Project.Format.SINGLE),
                    'tagline': item['tagline'],
                    'delivery_formats': item.get('delivery_formats', ''),
                    'is_published': True,
                    'details': {'seeded': True},
                },
            )

            if not was_created:
                project.title = item['title']
                project.category = item['category']
                project.format = item.get('format', Project.Format.SINGLE)
                project.tagline = item['tagline']
                project.delivery_formats = item.get('delivery_formats', '')
                project.is_published = True

            project.details = {
                'seeded': True,
                'meta': item['meta'],
            }
            if item.get('overview'):
                project.details['overview'] = item['overview']
            elif item.get('description'):
                project.details['description'] = item['description']
            if item.get('highlights'):
                project.details['highlights'] = item['highlights']
            if item.get('additional'):
                project.details['additional'] = item['additional']
            if item.get('tools'):
                project.details['tools'] = item['tools']

            image_bytes = self._build_poster(
                title=item['title'],
                category=project.get_category_display(),
                background=item['color'],
                accent=item['accent'],
                cover_style=item['category'] == Project.Category.COMIC,
            )
            project.thumbnail.save(
                f'{slug}-thumbnail.jpg',
                ContentFile(image_bytes),
                save=False,
            )
            project.featured_image.save(
                f'{slug}-featured.jpg',
                ContentFile(image_bytes),
                save=False,
            )
            project.save()

            project.media.all().delete()
            project.comic_pages.all().delete()
            project.episodes.all().delete()

            if item.get('format') == Project.Format.SERIES and item.get('issues'):
                issue_count = len(item['issues'])
                for issue_index, issue in enumerate(item['issues'], start=1):
                    issue_bytes = self._build_poster(
                        title=issue['title'],
                        category=f"Issue {issue_index:02d}",
                        background=item['color'],
                        accent=item['accent'],
                        cover_style=True,
                    )
                    episode = SeriesEpisode.objects.create(
                        project=project,
                        number=issue_index,
                        title=issue['title'],
                        tagline=issue.get('tagline', ''),
                    )
                    episode.thumbnail.save(
                        f'{slug}-issue-{issue_index:02d}-thumb.jpg',
                        ContentFile(issue_bytes),
                        save=False,
                    )
                    episode.featured_image.save(
                        f'{slug}-issue-{issue_index:02d}-cover.jpg',
                        ContentFile(issue_bytes),
                        save=True,
                    )
                    page_total = issue.get('pages', 0)
                    for page_index in range(1, page_total + 1):
                        page_bytes = self._build_comic_page(
                            title=issue['title'],
                            page_number=page_index,
                            total=page_total,
                            background=item['color'],
                            accent=item['accent'],
                        )
                        comic_page = ComicPage.objects.create(
                            episode=episode,
                            page_number=page_index,
                        )
                        comic_page.image.save(
                            f'{slug}-issue-{issue_index:02d}-page-{page_index:02d}.jpg',
                            ContentFile(page_bytes),
                            save=True,
                        )
                media_type = f'comic series ({issue_count} issues)'
            elif item.get('format') == Project.Format.SERIES and item.get('episodes'):
                episode_count = len(item['episodes'])
                episode_label = 'Cut' if item['category'] == Project.Category.ADVERTISING else 'Episode'
                for episode_index, episode_item in enumerate(item['episodes'], start=1):
                    episode_bytes = self._build_poster(
                        title=episode_item['title'],
                        category=f'{episode_label} {episode_index:02d}',
                        background=item['color'],
                        accent=item['accent'],
                    )
                    episode = SeriesEpisode.objects.create(
                        project=project,
                        number=episode_index,
                        title=episode_item['title'],
                        tagline=episode_item.get('tagline', ''),
                    )
                    episode.thumbnail.save(
                        f'{slug}-episode-{episode_index:02d}-thumb.jpg',
                        ContentFile(episode_bytes),
                        save=False,
                    )
                    episode.featured_image.save(
                        f'{slug}-episode-{episode_index:02d}-cover.jpg',
                        ContentFile(episode_bytes),
                        save=True,
                    )
                    if episode_item.get('video_url'):
                        video_bytes = self._download_file(episode_item['video_url'])
                        media = ProjectMedia.objects.create(
                            project=project,
                            episode=episode,
                            sort_order=0,
                        )
                        media.media_file.save(
                            f'{slug}-episode-{episode_index:02d}.mp4',
                            ContentFile(video_bytes),
                            save=True,
                        )
                if item['category'] == Project.Category.ADVERTISING:
                    media_type = f'advertising series ({episode_count} cuts)'
                else:
                    media_type = f'film series ({episode_count} episodes)'
            elif item['category'] == Project.Category.COMIC:
                page_count = item.get('comic_pages', 0)
                for index in range(1, page_count + 1):
                    page_bytes = self._build_comic_page(
                        title=item['title'],
                        page_number=index,
                        total=page_count,
                        background=item['color'],
                        accent=item['accent'],
                    )
                    comic_page = ComicPage.objects.create(
                        project=project,
                        page_number=index,
                    )
                    comic_page.image.save(
                        f'{slug}-page-{index:02d}.jpg',
                        ContentFile(page_bytes),
                        save=True,
                    )
                media_type = f'comic ({page_count} pages)'
            elif item.get('video'):
                video_bytes = self._download_file(item['video_url'])
                media = ProjectMedia.objects.create(
                    project=project,
                    sort_order=0,
                )
                media.media_file.save(
                    f'{slug}-main.mp4',
                    ContentFile(video_bytes),
                    save=True,
                )
                media_type = 'video'
                self._seed_gallery(project, item, slug)
            else:
                media_type = 'image'
                self._seed_gallery(project, item, slug)

            created += 1
            self.stdout.write(self.style.SUCCESS(f'Seeded "{project.title}" ({media_type}).'))

        self.stdout.write(self.style.SUCCESS(f'Done. {created} projects ready for testing.'))

    def _seed_gallery(self, project, item, slug):
        gallery_items = item.get('gallery', [])
        for index, gallery_item in enumerate(gallery_items, start=1):
            image_bytes = self._build_gallery_slide(
                title=project.title,
                caption=gallery_item.get('caption', f'Gallery {index}'),
                background=item['color'],
                accent=item['accent'],
                index=index,
            )
            media = ProjectMedia.objects.create(
                project=project,
                sort_order=index,
                caption=gallery_item.get('caption', ''),
            )
            media.media_file.save(
                f'{slug}-gallery-{index:02d}.jpg',
                ContentFile(image_bytes),
                save=True,
            )

    def _build_gallery_slide(self, title, caption, background, accent, index):
        width, height = 1280, 960
        image = Image.new('RGB', (width, height), (12, 12, 16))
        draw = ImageDraw.Draw(image)

        draw.rectangle((48, 48, width - 48, height - 48), outline=accent, width=3)
        draw.rectangle((72, 72, width - 72, 120), fill=accent)
        draw.text((88, 86), f'GALLERY {index:02d}', fill=(20, 20, 24))
        draw.text((88, 160), title, fill=(240, 240, 240))
        draw.text((88, 220), caption[:72], fill=(180, 180, 180))
        draw.rectangle((88, 280, width - 88, height - 120), fill=background)

        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=90)
        return buffer.getvalue()

    def _build_poster(self, title, category, background, accent, cover_style=False):
        width, height = 1280, 720
        image = Image.new('RGB', (width, height), background)
        draw = ImageDraw.Draw(image)

        if cover_style:
            panel_left = 430
            panel_top = 48
            panel_right = 850
            panel_bottom = height - 48
            draw.rectangle(
                (panel_left, panel_top, panel_right, panel_bottom),
                fill=(18, 18, 22),
                outline=accent,
                width=4,
            )
            draw.rectangle((panel_left + 28, panel_top + 28, panel_right - 28, panel_top + 44), fill=accent)
            draw.text((panel_left + 28, panel_top + 72), 'ISSUE 01', fill=accent)
            draw.text((panel_left + 28, panel_top + 130), title, fill=(245, 245, 245))
            draw.text((panel_left + 28, panel_bottom - 56), 'COVER', fill=(180, 180, 180))
        else:
            draw.rectangle((56, 56, 180, 64), fill=accent)
            draw.text((56, 92), category.upper(), fill=accent)
            draw.text((56, 150), title, fill=(245, 245, 245))
            draw.text((56, height - 72), 'Simply Matata', fill=(180, 180, 180))

        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=90)
        return buffer.getvalue()

    def _build_comic_page(self, title, page_number, total, background, accent):
        width, height = 900, 1350
        image = Image.new('RGB', (width, height), (14, 14, 18))
        draw = ImageDraw.Draw(image)

        margin = 48
        draw.rectangle(
            (margin, margin, width - margin, height - margin),
            outline=accent,
            width=3,
        )
        draw.rectangle(
            (margin + 24, margin + 24, width - margin - 24, margin + 72),
            fill=accent,
        )
        draw.text((margin + 36, margin + 38), f'PAGE {page_number:02d}', fill=(20, 20, 24))
        draw.text((margin + 36, margin + 140), title.upper(), fill=(235, 235, 235))
        draw.text(
            (margin + 36, height - margin - 96),
            f'{page_number} / {total}',
            fill=(180, 180, 180),
        )
        draw.line(
            (margin + 36, margin + 220, width - margin - 36, margin + 220),
            fill=(60, 60, 68),
            width=2,
        )
        draw.rectangle(
            (margin + 36, margin + 260, width - margin - 36, height - margin - 140),
            fill=background,
        )

        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=90)
        return buffer.getvalue()

    def _download_file(self, url):
        self.stdout.write(f'Downloading {url} ...')
        with urllib.request.urlopen(url, timeout=60) as response:
            return response.read()
