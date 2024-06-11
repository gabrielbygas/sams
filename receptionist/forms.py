from django import forms
from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'message': forms.Textarea(attrs={'cols': 80, 'rows': 5, 'class': 'form-control', 'required': True}),
        }