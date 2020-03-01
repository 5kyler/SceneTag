from django import forms
from .models import ShotRotation, ObjectTag, AutoObjectTag, ManualTagResult


class ShotRotationForm(forms.ModelForm):
    class Meta:
        model = ShotRotation
        fields = ('video', 'shot', 'rotation', 'parameter')


class ObjectTagForm(forms.ModelForm):
    class Meta:
        model = ObjectTag
        fields = ('x1', 'y1', 'w', 'h', 'label')


class ObjectTaggingForm(forms.ModelForm):
    class Meta:
        model = AutoObjectTag
        fields = ('video', 'frame', 'threshold', 'module_name')


class ResultTagForm(forms.ModelForm):
    class Meta:
        model = ManualTagResult
        fields = ('manual_module_name', 'manual_description', 'manual_score')
