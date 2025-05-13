from django.core.management.base import BaseCommand 
from Notebooks.models import Notebook, Scan
import os

class Command(BaseCommand):
    help = 'Scans the Notebook image file, creating records for new hits'

    def handle(self, *args, **kwargs):
        base = '/Volumes/Users/tslarkin/Projects/CFMulks/CFMulks/static/img/'
        for file in os.listdir(base):
            if file[0] == '.':
                continue
            # Every notebook has a unique name, therefore 
            # the query set can have only 0 or 1 hits.
            hits = Notebook.objects.filter(name = file)
            if not hits.exists():
                current_notebook = Notebook.objects.create(name=file)
            else:
                current_notebook = hits.first()
            print(current_notebook)
            path = base+file
            current_notebook_pages = { p.file for p in current_notebook.scan_set.all() }
            if os.path.isdir(path):
                if file[0] == '.':
                    continue
                current_files = set(os.listdir(path))
                to_delete = current_notebook_pages - current_files
                to_add = current_files - current_notebook_pages
                for img_name in to_add:
                    if img_name[0] == '.':
                        continue
                    Scan.objects.create(file=img_name, notebook=current_notebook)
                current_notebook.scan_set.filter(file__in=to_delete).delete()
