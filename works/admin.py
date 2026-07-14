from django.contrib import admin
from django.utils.html import format_html

from .forms import ProjectAdminForm, ProjectMediaForm
from .models import AnonymousComment, ComicPage, Project, ProjectMedia, SeriesEpisode

admin.site.site_header = 'SimplyMatata'
admin.site.site_title = 'SimplyMatata Admin'
admin.site.index_title = 'Manage projects and content'


class ProjectMediaInline(admin.TabularInline):
    model = ProjectMedia
    form = ProjectMediaForm
    extra = 1
    fields = ('media_file', 'youtube_url', 'caption', 'sort_order')
    ordering = ('sort_order', 'id')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(episode__isnull=True)


class ComicPageInline(admin.TabularInline):
    model = ComicPage
    extra = 1
    fields = ('page_number', 'image')
    ordering = ('page_number',)
    fk_name = 'project'
    verbose_name = 'Page'
    verbose_name_plural = 'Comic pages'


class SeriesEpisodeInline(admin.TabularInline):
    model = SeriesEpisode
    extra = 1
    fields = ('number', 'title', 'tagline', 'thumbnail', 'featured_image')
    ordering = ('number',)
    show_change_link = True
    verbose_name = 'Episode'
    verbose_name_plural = 'Episodes / issues / cuts'


class EpisodeMediaInline(admin.TabularInline):
    model = ProjectMedia
    form = ProjectMediaForm
    extra = 1
    fields = ('media_file', 'youtube_url', 'caption', 'sort_order')
    fk_name = 'episode'
    verbose_name = 'Media item'
    verbose_name_plural = 'Episode media'


class EpisodeComicPageInline(admin.TabularInline):
    model = ComicPage
    extra = 1
    fields = ('page_number', 'image')
    ordering = ('page_number',)
    fk_name = 'episode'
    verbose_name = 'Page'
    verbose_name_plural = 'Issue pages'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = (
        'title',
        'category',
        'format',
        'homepage_slot',
        'is_published',
        'media_summary',
        'created_at',
    )
    list_filter = ('category', 'format', 'is_published', 'homepage_slot')
    list_editable = ('is_published',)
    search_fields = ('title', 'tagline', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'setup_guide')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    save_on_top = True

    class Media:
        js = ('js/admin-project-form.js',)

    @admin.display(description='Media')
    def media_summary(self, obj):
        if obj.is_series:
            count = obj.episode_count
            label = obj.episodes_plural_label
            return f'{count} {label}' if count else 'No episodes yet'
        if obj.is_comic:
            pages = obj.comic_pages.count()
            return f'{pages} page{"s" if pages != 1 else ""}' if pages else 'No pages yet'
        if obj.has_featured_video:
            return 'Video attached'
        gallery = len(obj.gallery_media)
        if gallery:
            return f'Image + {gallery} gallery item{"s" if gallery != 1 else ""}'
        return 'Image only'

    def setup_guide(self, obj):
        if not obj or not obj.pk:
            return (
                'Save the project first. Then add media below based on category and format.'
            )

        if obj.is_series:
            return format_html(
                '<strong>Series project.</strong> Add entries under <em>{}</em> below. '
                'Each entry gets its own video or comic pages.',
                obj.episodes_section_label,
            )

        if obj.is_film or obj.is_advertising:
            return format_html(
                '<strong>Single {}.</strong> Add one video file (or YouTube URL) under '
                '<em>Film video &amp; gallery</em> below. The first video becomes the main '
                'watch experience. Extra items appear in the gallery.',
                'film' if obj.is_film else 'ad',
            )

        if obj.is_comic:
            return (
                'Single comic. Add pages under Comic pages below. '
                'Page 1 is typically used as the cover.'
            )

        return (
            'Add optional gallery media below. Software and lab projects use the '
            'featured image as the hero.'
        )

    setup_guide.short_description = 'How to add media'

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': (
                    'title',
                    'slug',
                    'category',
                    'tagline',
                    'is_published',
                    'homepage_slot',
                    'created_at',
                ),
            }),
        ]

        show_format = obj is None or obj.supports_format
        show_delivery = obj is None or obj.is_advertising

        format_fields = []
        if show_format:
            format_fields.append('format')
        if show_delivery:
            format_fields.append('delivery_formats')

        if format_fields:
            fieldsets.append(('Format', {
                'fields': tuple(format_fields),
                'description': (
                    'Film / advertising / comic only. '
                    '<strong>Single</strong> = one film, ad, or comic — add video or pages on this screen. '
                    '<strong>Series</strong> = multiple episodes, cuts, or issues — save first, then add entries below.'
                ),
            }))

        fieldsets.extend([
            ('Cover art', {
                'fields': ('thumbnail', 'featured_image'),
                'description': (
                    'Card thumbnail: 4:5 portrait (1080×1350) for works cards and homepage. '
                    'Detail cover: 16:9 (1920×1080) for film/ad project pages, or 4:5 for comics. '
                    'Provide at least one — if only one is uploaded, it is reused everywhere.'
                ),
            }),
            ('About this project (optional)', {
                'fields': (
                    'overview',
                    'additional',
                    'tools',
                    'meta_year',
                    'meta_role',
                    'meta_client',
                ),
                'classes': ('collapse',),
                'description': (
                    'Optional project details. Which fields apply depends on the category selected above.'
                ),
            }),
        ])

        if obj:
            fieldsets.insert(2, ('Media setup', {
                'fields': ('setup_guide',),
            }))

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if not obj:
            fields = [field for field in fields if field != 'setup_guide']
        return fields

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'delivery_formats':
            formfield.help_text = 'Comma-separated, e.g. YouTube, TV, Reels.'
        if db_field.name == 'format':
            formfield.help_text = (
                'Single = one film or ad with video on this page. '
                'Series = multiple episodes/cuts managed below.'
            )
        if db_field.name == 'thumbnail':
            formfield.help_text = (
                '4:5 card cover (1080×1350). Shown on works cards and homepage.'
            )
        if db_field.name == 'featured_image':
            formfield.help_text = (
                'Detail-page cover. 16:9 (1920×1080) for film and advertising; 4:5 for comics. '
                'Only shown on the project page when uploaded.'
            )
        if db_field.name == 'homepage_slot':
            formfield.help_text = (
                'Choose slot 1, 2, or 3 to feature this project on the homepage. '
                'Leave blank to hide it from Selected Works.'
            )
        return formfield

    def get_inlines(self, request, obj):
        if not obj:
            return [ProjectMediaInline]

        if obj.is_series:
            return [SeriesEpisodeInline]

        if obj.is_comic:
            return [ComicPageInline]

        return [ProjectMediaInline]

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        if obj and obj.is_video_story and obj.is_single:
            for inline in inline_instances:
                if isinstance(inline, ProjectMediaInline):
                    inline.verbose_name = 'Video / gallery item'
                    inline.verbose_name_plural = 'Film video & gallery'
        return inline_instances


@admin.register(SeriesEpisode)
class SeriesEpisodeAdmin(admin.ModelAdmin):
    list_display = ('project', 'number', 'title', 'episode_media_summary')
    list_filter = ('project__category', 'project')
    search_fields = ('title', 'tagline', 'project__title')
    autocomplete_fields = ('project',)
    ordering = ('project', 'number')
    save_on_top = True
    fieldsets = (
        (None, {
            'fields': ('project', 'number', 'title', 'tagline'),
        }),
        ('Cover art', {
            'fields': ('thumbnail', 'featured_image'),
            'description': (
                'Card thumbnail: 4:5 for episode cards. Detail cover: 16:9 for film/ad episodes. '
                'Provide at least one — the other is reused as a fallback.'
            ),
        }),
    )

    def get_inlines(self, request, obj):
        if obj and obj.project.is_comic:
            return [EpisodeComicPageInline]
        return [EpisodeMediaInline]

    @admin.display(description='Media')
    def episode_media_summary(self, obj):
        if obj.project.is_comic:
            return f'{obj.comic_page_count} pages'
        if obj.has_featured_video:
            return 'Video'
        return 'Image only'


@admin.register(ComicPage)
class ComicPageAdmin(admin.ModelAdmin):
    list_display = ('owner', 'page_number', 'image')
    list_filter = ('project', 'episode__project')
    search_fields = ('project__title', 'episode__title')
    ordering = ('page_number',)
    autocomplete_fields = ('project', 'episode')

    @admin.display(description='Owner')
    def owner(self, obj):
        return obj.episode or obj.project


@admin.register(ProjectMedia)
class ProjectMediaAdmin(admin.ModelAdmin):
    form = ProjectMediaForm
    list_display = ('project', 'episode', 'media_type', 'caption', 'sort_order')
    list_filter = ('project__category',)
    search_fields = ('project__title', 'episode__title', 'caption')
    ordering = ('project', 'sort_order', 'id')
    autocomplete_fields = ('project', 'episode')
    fields = ('project', 'episode', 'media_file', 'youtube_url', 'caption', 'sort_order')

    @admin.display(description='Type')
    def media_type(self, obj):
        if obj.is_video:
            return 'Video file'
        if obj.youtube_url:
            return 'YouTube'
        if obj.is_image:
            return 'Image'
        return 'File'


@admin.register(AnonymousComment)
class AnonymousCommentAdmin(admin.ModelAdmin):
    list_display = ('project', 'content_preview', 'ip_address', 'created_at')
    list_filter = ('project', 'created_at')
    search_fields = ('content', 'ip_address')
    readonly_fields = ('project', 'content', 'ip_address', 'user_agent', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    @admin.display(description='Content')
    def content_preview(self, obj):
        return obj.content[:80] + ('…' if len(obj.content) > 80 else '')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
