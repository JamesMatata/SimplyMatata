from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags


class AnonymousCommentForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Leave a thought…',
            'class': 'w-full rounded-lg border border-white/20 bg-black/30 px-4 py-3 text-white placeholder-white/40 focus:border-red-600 focus:outline-none',
        }),
        max_length=2000,
    )
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}),
    )

    def clean_content(self):
        content = strip_tags(self.cleaned_data.get('content', '')).strip()
        if not content:
            raise ValidationError('Comment cannot be empty.')
        if len(content) < 2:
            raise ValidationError('Comment is too short.')
        return content

    @property
    def honeypot_triggered(self):
        return bool(self.data.get('website'))
