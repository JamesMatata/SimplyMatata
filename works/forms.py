from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from .models import AnonymousComment, Project


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


class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

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
