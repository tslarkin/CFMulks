from django.core.management.base import BaseCommand 
from Notebooks.models import Notebook, Scan
import os

class Command(BaseCommand):
    help = 'Indexes the Scan model by file name'

    def handle(self, *args, **kwargs):
        hits = Scan.objects.filter(notebook__name="3").order_by('file')
        index = 0
        for page in hits:
            page.seq_num = index
            page.save()
            index += 1
        