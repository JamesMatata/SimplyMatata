from django.contrib import admin

from .models import AnonymousComment, ComicPage, Project, ProjectMedia, SeriesEpisode


class ProjectMediaInline(admin.TabularInline):
    model = ProjectMedia
    extra = 1
    fields = ('media_file', 'youtube_url', 'caption', 'sort_order')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(episode__isnull=True)


class ComicPageInline(admin.TabularInline):
    model = ComicPage
    extra = 1
    fields = ('page_number', 'image')
    ordering = ('page_number',)
    fk_name = 'project'


class SeriesEpisodeInline(admin.TabularInline):
    model = SeriesEpisode
    extra = 1
    fields = ('number', 'title', 'tagline', 'thumbnail', 'featured_image')
    ordering = ('number',)
    show_change_link = True


class EpisodeMediaInline(admin.TabularInline):
    model = ProjectMedia
    extra = 1
    fields = ('media_file', 'youtube_url', 'caption', 'sort_order')
    fk_name = 'episode'


class EpisodeComicPageInline(admin.TabularInline):
    model = ComicPage
    extra = 1
    fields = ('page_number', 'image')
    ordering = ('page_number',)
    fk_name = 'episode'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'format', 'is_published', 'created_at')
    list_filter = ('category', 'format', 'is_published')
    search_fields = ('title', 'tagline', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    fields = (
        'title',
        'slug',
        'category',
        'format',
        'tagline',
        'delivery_formats',
        'thumbnail',
        'featured_image',
        'details',
        'is_published',
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'details':
            formfield.help_text = (
                'JSON project content. Supported keys: '
                'overview (markdown), highlights [{label, value}], '
                'additional (markdown), tools [strings], '
                'meta {year, role, client}, description (legacy overview fallback).'
            )
        if db_field.name == 'delivery_formats':
            formfield.help_text = (
                'Advertising only. Comma-separated delivery formats, '
                'e.g. YouTube, TV, Reels, Social.'
            )
        if db_field.name == 'format':
            formfield.help_text = (
                'Single = one film, ad, or comic. Series = multiple episodes/issues/cuts '
                'managed under Episodes below.'
            )
        return formfield

    def get_inlines(self, request, obj):
        if not obj:
            return [ProjectMediaInline]

        if obj.is_series:
            return [SeriesEpisodeInline]

        if obj.category == Project.Category.COMIC:
            return [ComicPageInline]

        return [ProjectMediaInline]


@admin.register(SeriesEpisode)
class SeriesEpisodeAdmin(admin.ModelAdmin):
    list_display = ('project', 'number', 'title', 'episode_media_summary')
    list_filter = ('project__category', 'project')
    search_fields = ('title', 'tagline', 'project__title')
    ordering = ('project', 'number')
    fields = ('project', 'number', 'title', 'tagline', 'thumbnail', 'featured_image')

    def get_inlines(self, request, obj):
        if obj and obj.project.is_comic:
            return [EpisodeComicPageInline]
        return [EpisodeMediaInline]

    def episode_media_summary(self, obj):
        if obj.project.is_comic:
            return f'{obj.comic_page_count} pages'
        if obj.has_featured_video:
            return 'Video'
        return 'Image'

    episode_media_summary.short_description = 'Media'


@admin.register(ComicPage)
class ComicPageAdmin(admin.ModelAdmin):
    list_display = ('owner', 'page_number', 'image')
    list_filter = ('project', 'episode__project')
    search_fields = ('project__title', 'episode__title')
    ordering = ('page_number',)

    def owner(self, obj):
        return obj.episode or obj.project

    owner.short_description = 'Owner'


@admin.register(AnonymousComment)
class AnonymousCommentAdmin(admin.ModelAdmin):
    list_display = ('project', 'content_preview', 'ip_address', 'created_at')
    list_filter = ('project', 'created_at')
    search_fields = ('content', 'ip_address')
    readonly_fields = ('project', 'content', 'ip_address', 'user_agent', 'created_at')

    def content_preview(self, obj):
        return obj.content[:80] + ('…' if len(obj.content) > 80 else '')

    content_preview.short_description = 'Content'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
