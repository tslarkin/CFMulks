from django.db import models

class Notebook(models.Model):
    name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)

class Scan(models.Model):
    file = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    notebook = models.ForeignKey(Notebook, on_delete=models.SET_NULL, null=True)
    seq_num = models.CharField(20, blank=True)
    transcription = models.TextField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        f"Scan {self.name}"
