from django import forms
from django_select2.forms import Select2TagWidget
from .models import Scan
from taggit.models import Tag
from dal import autocomplete
from taggit.managers import TaggableManager

class ScanTagsForm(autocomplete.FutureModelForm):

    class Meta:
        model = Scan  # This line is crucial
        fields = ('tags',)
        widgets = {
            'tags': autocomplete.TaggitSelect2(url='tag-autocomplete'),
        }

class ScanForm(autocomplete.FutureModelForm):

    class Meta:
        model=Scan
        fields = ('__all__')
        widgets = {
            'tags': autocomplete.TaggitSelect2(url='tag-autocomplete'),
        }