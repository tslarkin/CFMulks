from django import forms
from django_select2.forms import Select2TagWidget
from .models import Scan
from taggit.models import Tag
from dal import autocomplete
from taggit.managers import TaggableManager

class ScanTagsForm(autocomplete.FutureModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Assuming 'related_field' is the field with autocomplete
        self.fields['tags'].help_text = ''

    class Meta:
        model = Scan  # This line is crucial
        fields = ('tags', )
        labels = {
            'tags': '',
        }

        widgets = {
            'tags': autocomplete.TaggitSelect2(url='tag-autocomplete',
                attrs={ 'data-minimum-input-length': 2,
                        # This attribute is crucial for inline tag creation (tagging)
                        'data-tags': ',', 
                    }
            ),
        }

class ScanForm(autocomplete.FutureModelForm):

    class Meta:
        model=Scan
        fields = ('tags',)
        widgets = {
            'tags': autocomplete.TaggitSelect2(url='tag-autocomplete'),
        }

class Autotags(autocomplete.FutureModelForm):
    class Meta:
        model = Scan
        fields = ('tags',)
        widgets = {
            'tags': autocomplete.TaggitSelect2(url='tag-autocomplete'),
        }
