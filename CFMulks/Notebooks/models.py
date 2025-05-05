from django.db import models

class Notebook(models.Model):
    name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)

class Page(models.Model):
    name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    notebook = models.ForeignKey(Notebook, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        f"Page {self.name}"
