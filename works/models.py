import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from .details import normalize_details
from .media_utils import media_file_url
from .validators import validate_image_upload, validate_media_upload


class Project(models.Model):
    class Category(models.TextChoices):
        SOFTWARE = 'software', 'Software'
        FILM = 'film', 'Film'
        COMIC = 'comic', 'Comic'
        ADVERTISING = 'advertising', 'Advertising'
        LAB = 'lab', 'Lab'

    class Format(models.TextChoices):
        SINGLE = 'single', 'Single'
        SERIES = 'series', 'Series'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    format = models.CharField(
        max_length=20,
        choices=Format.choices,
        default=Format.SINGLE,
        help_text='Single or series. Applies to film and comic projects.',
    )
    tagline = models.CharField(max_length=300)
    delivery_formats = models.CharField(
        max_length=500,
        blank=True,
        help_text='For advertising projects: comma-separated list, e.g. YouTube, TV, Reels.',
    )
    thumbnail = models.ImageField(
        upload_to='projects/thumbnails/',
        blank=True,
        validators=[validate_image_upload],
        help_text='Optional 4:5 card cover (1080×1350). Used on works cards and homepage.',
    )
    featured_image = models.ImageField(
        upload_to='projects/featured/',
        blank=True,
        validators=[validate_image_upload],
        help_text='Optional detail-page cover. Use 16:9 (1920×1080) for film and advertising; 4:5 for comics.',
    )
    details = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=False)
    homepage_slot = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=[(1, 'Homepage slot 1'), (2, 'Homepage slot 2'), (3, 'Homepage slot 3')],
        help_text='Pin this project to a homepage slot. Each slot can only hold one project.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['homepage_slot'],
                condition=models.Q(homepage_slot__isnull=False),
                name='unique_homepage_slot',
            ),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.details = normalize_details(self.details)
        super().save(*args, **kwargs)

    @property
    def featured_video(self):
        if self.is_series:
            return None
        for item in self.media.all():
            if item.episode_id is None and item.is_video:
                return item
        return None

    @property
    def has_featured_video(self):
        return self.featured_video is not None

    @property
    def gallery_media(self):
        featured = self.featured_video
        return [
            item for item in self.media.all()
            if item.episode_id is None
            and not (featured and item.pk == featured.pk)
        ]

    @property
    def show_media_gallery(self):
        if self.is_comic or self.is_series:
            return False
        return bool(self.gallery_media)

    @property
    def is_comic(self):
        return self.category == self.Category.COMIC

    @property
    def is_film(self):
        return self.category == self.Category.FILM

    @property
    def is_advertising(self):
        return self.category == self.Category.ADVERTISING

    @property
    def is_video_story(self):
        return self.is_film or self.is_advertising

    @property
    def supports_format(self):
        return self.is_comic or self.is_video_story

    @property
    def is_series(self):
        return self.supports_format and self.format == self.Format.SERIES

    @property
    def is_single(self):
        return not self.is_series

    @property
    def format_label(self):
        if not self.supports_format:
            return ''
        return 'Series' if self.is_series else 'Single'

    @property
    def episode_label(self):
        if self.is_comic:
            return 'issue'
        if self.is_advertising:
            return 'cut'
        if self.is_film:
            return 'episode'
        return 'part'

    @property
    def episodes_section_label(self):
        if self.is_comic:
            return 'Issues'
        if self.is_advertising:
            return 'Cuts'
        return 'Episodes'

    @property
    def episodes_action_verb(self):
        return 'read' if self.is_comic else 'watch'

    @property
    def episodes_plural_label(self):
        label = self.episode_label
        if label == 'issue':
            return 'issues'
        if label == 'episode':
            return 'episodes'
        return 'parts'

    @property
    def episode_count(self):
        if hasattr(self, '_episode_count'):
            return self._episode_count
        return self.episodes.count()

    @property
    def show_episodes(self):
        return self.is_series and self.episode_count > 0

    @property
    def comic_page_count(self):
        if hasattr(self, '_comic_page_count'):
            return self._comic_page_count
        if self.is_series:
            return sum(episode.comic_page_count for episode in self.episodes.all())
        return self.comic_pages.count()

    @property
    def show_comic_reader(self):
        return self.is_comic and self.is_single and self.comic_pages.count() > 0

    @property
    def card_thumbnail(self):
        if media_file_url(self.thumbnail):
            return self.thumbnail
        if media_file_url(self.featured_image):
            return self.featured_image
        return None

    @property
    def hero_image(self):
        if media_file_url(self.featured_image):
            return self.featured_image
        if media_file_url(self.thumbnail):
            return self.thumbnail
        return None

    @property
    def has_wide_hero(self):
        return self.is_video_story and bool(media_file_url(self.featured_image))

    @property
    def hero_poster(self):
        return self.hero_image or self.card_thumbnail

    @property
    def track(self):
        if self.category == self.Category.SOFTWARE:
            return 'software'
        return 'storytelling'

    @property
    def safe_details(self):
        return normalize_details(self.details)

    @property
    def card_thumbnail_url(self):
        return media_file_url(self.card_thumbnail)

    @property
    def hero_image_url(self):
        return media_file_url(self.hero_image)

    @property
    def featured_image_url(self):
        return media_file_url(self.featured_image) or media_file_url(self.thumbnail)

    @property
    def description(self):
        value = self.safe_details.get('description', '')
        return value.strip() if isinstance(value, str) else ''

    @property
    def overview(self):
        value = self.safe_details.get('overview') or self.safe_details.get('description') or ''
        return value.strip() if isinstance(value, str) else ''

    @property
    def highlights(self):
        items = self.safe_details.get('highlights', [])
        if not isinstance(items, list):
            return []
        highlights = []
        for item in items:
            if not isinstance(item, dict):
                continue
            label = str(item.get('label', '')).strip()
            value = str(item.get('value') or item.get('body') or '').strip()
            if label and value:
                highlights.append({'label': label, 'value': value})
        return highlights

    @property
    def additional_notes(self):
        value = self.safe_details.get('additional', '')
        return value.strip() if isinstance(value, str) else ''

    @property
    def tools(self):
        items = self.safe_details.get('tools', [])
        if isinstance(items, str):
            return [part.strip() for part in items.split(',') if part.strip()]
        if not isinstance(items, list):
            return []
        return [str(item).strip() for item in items if str(item).strip()]

    @property
    def is_software(self):
        return self.category == self.Category.SOFTWARE

    @property
    def has_about_content(self):
        return bool(self.overview or self.highlights or self.additional_notes)

    @property
    def show_tools(self):
        return self.is_software and bool(self.tools)

    @property
    def meta(self):
        value = self.safe_details.get('meta', {})
        return value if isinstance(value, dict) else {}

    @property
    def delivery_format_list(self):
        if not self.delivery_formats:
            return []
        return [
            part.strip()
            for part in self.delivery_formats.split(',')
            if part.strip()
        ]

    @property
    def show_delivery_formats(self):
        return self.is_advertising and bool(self.delivery_format_list)

    @property
    def format_badge(self):
        if not self.supports_format:
            return ''
        if self.is_series and self.episode_count:
            label = self.episodes_plural_label.title()
            return f'Series · {self.episode_count} {label}'
        if self.is_comic and self.is_single and self.comic_page_count:
            return f'{self.comic_page_count} page{"s" if self.comic_page_count != 1 else ""}'
        if self.is_film and self.is_single:
            return 'Single'
        if self.is_advertising and self.is_single:
            return ''
        return self.format_label

    def clean(self):
        super().clean()
        if not media_file_url(self.thumbnail) and not media_file_url(self.featured_image):
            raise ValidationError(
                'Provide at least one cover image: a 4:5 card thumbnail and/or a detail-page cover.'
            )


class SeriesEpisode(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='episodes',
    )
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    tagline = models.CharField(max_length=300, blank=True)
    thumbnail = models.ImageField(
        upload_to='projects/episodes/thumbnails/',
        blank=True,
        validators=[validate_image_upload],
        help_text='Optional 4:5 card cover for episode cards.',
    )
    featured_image = models.ImageField(
        upload_to='projects/episodes/featured/',
        blank=True,
        validators=[validate_image_upload],
        help_text='Optional detail cover. Use 16:9 for film/ad episodes; 4:5 for comics.',
    )

    class Meta:
        ordering = ['number']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'number'],
                name='unique_series_episode_number',
            ),
        ]

    def __str__(self):
        return f'{self.project.title} — {self.display_number}'

    @property
    def display_number(self):
        return f'{self.number:02d}'

    @property
    def card_thumbnail(self):
        if media_file_url(self.thumbnail):
            return self.thumbnail
        if media_file_url(self.featured_image):
            return self.featured_image
        return None

    @property
    def hero_image(self):
        if media_file_url(self.featured_image):
            return self.featured_image
        if media_file_url(self.thumbnail):
            return self.thumbnail
        return None

    @property
    def has_wide_hero(self):
        return self.project.is_video_story and bool(media_file_url(self.featured_image))

    @property
    def hero_poster(self):
        return self.hero_image or self.card_thumbnail

    @property
    def card_thumbnail_url(self):
        return media_file_url(self.card_thumbnail)

    @property
    def featured_video(self):
        for item in self.media.all():
            if item.is_video:
                return item
        return None

    @property
    def has_featured_video(self):
        return self.featured_video is not None

    @property
    def comic_page_count(self):
        return self.comic_pages.count()

    @property
    def show_comic_reader(self):
        return self.project.is_comic and self.comic_page_count > 0

    def clean(self):
        super().clean()
        if not media_file_url(self.thumbnail) and not media_file_url(self.featured_image):
            raise ValidationError(
                'Provide at least one cover image: a 4:5 card thumbnail and/or a detail-page cover.'
            )


class ProjectMedia(models.Model):
    VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov', '.m4v', '.ogv'}

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='media',
    )
    episode = models.ForeignKey(
        SeriesEpisode,
        on_delete=models.CASCADE,
        related_name='media',
        null=True,
        blank=True,
    )
    media_file = models.FileField(
        upload_to='projects/media/',
        blank=True,
        validators=[validate_media_upload],
    )
    youtube_url = models.URLField(blank=True)
    caption = models.CharField(max_length=200, blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        if self.episode_id:
            return f'{self.episode} — media #{self.pk}'
        return f'{self.project.title} — media #{self.pk}'

    @property
    def is_video(self):
        if not self.media_file:
            return False
        try:
            name = self.media_file.name or ''
            if '.' not in name:
                return False
            extension = name.rsplit('.', 1)[-1].lower()
            return f'.{extension}' in self.VIDEO_EXTENSIONS
        except (AttributeError, IndexError):
            return False

    @property
    def is_image(self):
        if not self.media_file:
            return False
        try:
            name = self.media_file.name or ''
            if '.' not in name:
                return False
            extension = name.rsplit('.', 1)[-1].lower()
            return extension in {'jpg', 'jpeg', 'png', 'gif', 'webp', 'avif'}
        except (AttributeError, IndexError):
            return False

    @property
    def youtube_embed_url(self):
        if not self.youtube_url:
            return ''
        url = self.youtube_url.strip()
        if '/embed/' in url:
            return url
        video_id = ''
        if 'youtu.be/' in url:
            video_id = url.rsplit('youtu.be/', 1)[-1].split('?')[0]
        elif 'v=' in url:
            video_id = url.split('v=', 1)[-1].split('&')[0]
        if not video_id:
            return url
        return f'https://www.youtube.com/embed/{video_id}'

    def clean(self):
        has_file = bool(self.media_file and getattr(self.media_file, 'name', ''))
        has_youtube = bool((self.youtube_url or '').strip())
        if not has_file and not has_youtube:
            if not self.pk:
                return
            raise ValidationError('Either a media file or a YouTube URL is required.')
        if has_file and has_youtube:
            raise ValidationError('Provide either a media file or a YouTube URL, not both.')


class ComicPage(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='comic_pages',
        null=True,
        blank=True,
    )
    episode = models.ForeignKey(
        SeriesEpisode,
        on_delete=models.CASCADE,
        related_name='comic_pages',
        null=True,
        blank=True,
    )
    page_number = models.PositiveIntegerField()
    image = models.ImageField(
        upload_to='projects/comics/',
        validators=[validate_image_upload],
    )

    class Meta:
        ordering = ['page_number']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'page_number'],
                condition=models.Q(episode__isnull=True),
                name='unique_comic_page_number',
            ),
            models.UniqueConstraint(
                fields=['episode', 'page_number'],
                condition=models.Q(episode__isnull=False),
                name='unique_episode_comic_page_number',
            ),
        ]

    def clean(self):
        if bool(self.project_id) == bool(self.episode_id):
            raise ValidationError('Assign comic pages to either a project or an episode, not both.')

    def __str__(self):
        owner = self.episode or self.project
        return f'{owner} — page {self.page_number}'


class AnonymousComment(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    content = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ip_address', 'created_at']),
        ]

    def __str__(self):
        return f'Comment on {self.project.title} ({self.created_at:%Y-%m-%d})'
