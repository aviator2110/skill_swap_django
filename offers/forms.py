from django import forms
from .models import Offer, Category, Level, Format


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = [
            'title',
            'category',
            'level',
            'format',
            'duration_minutes',
            'cover_image',
            'description',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Modern Python & Django Fundamentals'}),
            'duration_minutes': forms.NumberInput(attrs={'min': 15, 'step': 15}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe what students will learn, prerequisites, and lesson plan...'}),
        }

    def clean_duration_minutes(self):
        duration = self.cleaned_data.get('duration_minutes')
        if duration is not None and duration < 15:
            raise forms.ValidationError("Lesson duration must be at least 15 minutes.")
        return duration
