from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from .details import build_details_from_form, normalize_details
from .models import AnonymousComment, Project, ProjectMedia


class AnonymousCommentForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = AnonymousComment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Leave a note…',
            }),
        }

    @property
    def honeypot_triggered(self):
        return bool(self.data.get('website', '').strip())

    def clean_content(self):
        content = strip_tags(self.cleaned_data.get('content', '')).strip()
        if not content:
            raise ValidationError('Please write something before submitting.')
        if len(content) > 2000:
            raise ValidationError('Keep your note under 2000 characters.')
        return content


class ProjectMediaForm(forms.ModelForm):
    class Meta:
        model = ProjectMedia
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        media_file = cleaned_data.get('media_file')
        youtube_url = (cleaned_data.get('youtube_url') or '').strip()

        if not media_file and not youtube_url:
            if self.instance.pk:
                raise ValidationError('Either a media file or a YouTube URL is required.')
            return cleaned_data

        if media_file and youtube_url:
            raise ValidationError('Provide either a media file or a YouTube URL, not both.')

        cleaned_data['youtube_url'] = youtube_url
        return cleaned_data


class ProjectAdminForm(forms.ModelForm):
    overview = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text='Optional. Shown in the About section on the project page.',
    )
    additional = forms.CharField(
        label='Additional notes',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text='Optional. Extra notes below the overview.',
    )
    tools = forms.CharField(
        required=False,
        help_text='Optional. Comma-separated tools for software projects.',
    )
    meta_year = forms.CharField(label='Year', required=False, max_length=20)
    meta_role = forms.CharField(label='Role', required=False, max_length=120)
    meta_client = forms.CharField(label='Client', required=False, max_length=120)

    class Meta:
        model = Project
        exclude = ('details',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        details = normalize_details(
            self.instance.details if self.instance and self.instance.pk else {}
        )
        meta = details.get('meta', {})

        self.fields['overview'].initial = (
            details.get('overview') or details.get('description') or ''
        )
        self.fields['additional'].initial = details.get('additional', '')
        tools = details.get('tools', [])
        if isinstance(tools, list):
            self.fields['tools'].initial = ', '.join(str(item) for item in tools)
        self.fields['meta_year'].initial = meta.get('year', '')
        self.fields['meta_role'].initial = meta.get('role', '')
        self.fields['meta_client'].initial = meta.get('client', '')

    def save(self, commit=True):
        project = super().save(commit=False)
        project.details = build_details_from_form(self.cleaned_data)
        if commit:
            project.save()
            self.save_m2m()
        return project

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        project_format = cleaned_data.get('format')

        if category in {Project.Category.SOFTWARE, Project.Category.LAB}:
            cleaned_data['format'] = Project.Format.SINGLE
            cleaned_data['delivery_formats'] = ''

        if category != Project.Category.ADVERTISING:
            cleaned_data['delivery_formats'] = ''

        if (
            project_format == Project.Format.SERIES
            and category
            and category not in {
                Project.Category.FILM,
                Project.Category.COMIC,
                Project.Category.ADVERTISING,
            }
        ):
            raise ValidationError({
                'format': 'Series format is only available for Film, Comic, and Advertising projects.',
            })

        return cleaned_data
