from django.forms import ModelForm
from .models import Page

class UpdatePage(ModelForm):
    class Meta:
        model = Page
        fields = '__all__'
