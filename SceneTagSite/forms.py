from django import forms
from .models import ObjectTag, AutoObjectTag, AutoTagResult, IntervalVideo


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


class IntervalTagForm(forms.ModelForm):
    class Meta:
        model = IntervalVideo
        fields = ('tag1','tag2', 'tag3')

