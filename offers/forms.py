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


class BookingRequestForm(forms.ModelForm):
    class Meta:
        from .models import BookingRequest
        model = BookingRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'placeholder': 'Introduce yourself, specify your learning goals, and suggest your preferred dates/times...',
                'rows': 3,
            }),
        }


class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput(),
        initial=5,
        label="Rating"
    )

    class Meta:
        from .models import Review
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'placeholder': 'Share your learning experience, what you gained from this lesson, and your thoughts on the mentor...',
                'rows': 4,
            }),
        }


