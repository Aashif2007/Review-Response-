from django import forms
from .models import Business

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        exclude = ["owner", "created_at", "slug"]