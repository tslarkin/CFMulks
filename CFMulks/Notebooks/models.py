from django.db import models
import re
from roman import toRoman
from taggit.managers import TaggableManager

class Notebook(models.Model):
    name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)

    def roman_numeral(self):
        return toRoman(int(self.name))

class Scan(models.Model):
    file = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    notebook = models.ForeignKey(Notebook, on_delete=models.SET_NULL, null=True)
    seq_num = models.CharField(20, blank=True)
    transcription = models.TextField(blank=True)
    description = models.TextField(blank=True)
    tags = TaggableManager()

    def __str__(self):
        f"Scan {self.name}"

    def name(self):
        x = re.match(r'IMG(_\d{4}).jpe?g', self.file)
        return x[1]

