from django import forms
from .models import ShotRotation


class ShotRotationForm(forms.ModelForm):
    class Meta:
        model = ShotRotation
        fields = ('video', 'shot', 'rotation', 'parameter')



