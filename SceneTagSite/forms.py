from django import forms
from .models import ShotRotation, ObjectTag, AutoObjectTag, AutoTagResult


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
        model = AutoTagResult
        fields = ('auto_module_name', 'auto_description', 'auto_score')
