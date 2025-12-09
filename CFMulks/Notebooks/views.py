from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from .models import Notebook, Scan
from django.views.generic import View, ListView
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from roman import toRoman
from django.db.models import Q
import re
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.urls import reverse
import markdown2
from django.http import JsonResponse, HttpResponseBadRequest
from taggit.models import Tag
from .forms import ScanTagsForm
from dal import autocomplete

def search(request):
    return render(request, "Notebooks/search.html")

def resources(request):
    return render(request, "Notebooks/resources.html")

def biosketch(request):
    return render(request, "Notebooks/biosketch.html")

def searchresults(request):
    search = request.GET.get("search", "")
    if len(search) == 0:
        return HttpResponse(status = 200)
    characters = search.replace(" ", "")
    if len(characters) < 3:
        return HttpResponse(status = 200)
    search = re.sub(r'\s+', ' ', search)
    terms = search.split()
    bigQ = Q()
    for term in terms:
        q = Q(transcription__regex=r'(?i).*'+term + r"[a-z]*\s?.*")
        bigQ &= q
    records = Scan.objects.filter(bigQ).order_by('file')
    if len(records) == 0:
        return HttpResponse(status = 200)
    page_set = "-".join(str(record.id) for record in records)
    filter = list(records.values_list('id', flat=True))
    request.session['filter'] = filter
    hints = []
    index = 1
    for record in records:
        transcription_hints = get_hints('transcription', terms, index, record)
        index += 1
        hints+= transcription_hints
        hints += ['<div class="row" style="height: 30px"></div>']
    if len(hints) == 0:
        hints.append('<div class="row" style="text-align: center">No Matches Found</div>')
    return render(request, "partials/searchresults.html", {'hints': hints})

def get_hints(field_name, terms, index, record):
    field = getattr(record, field_name)
    if len(field) == 0:
        return []
    # delete Markdown headers
    pattern = r"^(\s*[a-zA-Z0-9]\s*\|)+(\s*[a-zA-Z0-9]\s*)$"
    field = re.sub(pattern, "", field, flags=re.MULTILINE)
    # remove carriage returns and new lines.
    field = field.replace('\r', ' ').replace('\n', ' ')
    # replace HTML tags with spaces
    pattern = r"(</?.+?>)"
    field = re.sub(pattern, " ", field)
    # replace runs of spaces with a single space
    field = re.sub(r"\s\s+", " ", field)
    # delete Markdown column specifiers
    pattern = r"(:?---+:?\|?)"
    field = re.sub(pattern, "", field)
    end = len(field)
    hints = []
    label_p = True
    notebook = record.notebook.id
    terms_str = " ".join(terms)
    for term in terms:
        pattern = "("+term+")"
        matches = re.finditer(pattern, field, re.IGNORECASE)
        for match in matches:
            spanstart, spanend = match.span()
            text = field[spanstart:spanend]
            a = max(spanstart - 80, 0)
            b = min(spanend + 80, end)
            prefix = " …" if a > 0 else " "
            suffix = "…" if b < end else ""
            label = ''
            if label_p:
                label = record.notebook.roman_numeral()+record.name() if field_name == "transcription" else "Notes"
                label_p = False
            url = f"/show_page_set/?page={index}&notebook={notebook}&terms={terms_str}"
            hint = f'<a class="row" style="color:black; text-decoration:none;" href="{url}">'\
                +f'<div class="cell label {field_name}">{label}</div>'\
                +f'<div class="cell {field_name}">{prefix}' + field[a:spanstart] + '<u>'+text+'</u>' + field[spanend:b] + suffix+'</div>'\
                +'</a>'
            hint = mark_safe(hint)
            hints.append(hint)
    return hints

def get_notes(field_name, terms, index, record):
    field = getattr(record, field_name)
    if len(field) == 0:
        return []
    # delete Markdown headers
    pattern = r"^(\s*[a-zA-Z0-9]\s*\|)+(\s*[a-zA-Z0-9]\s*)$"
    field = re.sub(pattern, "", field, flags=re.MULTILINE)
    # remove carriage returns and new lines.
    field = field.replace('\r', ' ').replace('\n', ' ')
    # replace HTML tags with spaces
    pattern = r"(</?.+?>)"
    field = re.sub(pattern, " ", field)
    # replace runs of spaces with a single space
    field = re.sub(r"\s\s+", " ", field)
    # delete Markdown column specifiers
    pattern = r"(:?---+:?\|?)"
    field = re.sub(pattern, "", field)
    field = markdown2.markdown(field, extras={'break-on_backslash': True, 'tables': None, 'strike': None})
    field = re.sub(r"</?p>", "", field)
    url = f"/show_page_set/{record.id}/"
    hint = f'<div class="row" style="color:black; text-decoration:none;">'\
        +f'<div class="cell label {field_name}">Notes</div>'\
        +f'<div class="cell {field_name}"> {field} </div>'\
        +'</div>'
    hint = mark_safe(hint)
    return [hint]
   
def show_page_set(request):
    if request.method == 'POST':
        new_page=request.POST.get('block_num')
        notebook_id = request.POST.get('notebook')
        terms = request.POST.get('terms')
        target = f"/show_page_set/?page={new_page}&notebook={notebook_id}&terms={terms}"
        return redirect(target)
    else:
        numbers = request.session['filter']
        notebook_id = request.GET.get('notebook')
        if len(numbers) > 0:
            pageset = Scan.objects.filter(pk__in=numbers).order_by('file')
        else:
            pageset = Scan.objects.filter(notebook__id=notebook_id).order_by('file')
        page_number = request.GET.get('page') or '1'
        terms = request.GET.get('terms') or ''
        paginator = Paginator(pageset,1)
        block_obj = paginator.get_page(page_number)
        page = block_obj.object_list[0]
        form = ScanTagsForm(instance=page)
        block_range = paginator.get_elided_page_range(number=page_number, on_each_side=1, on_ends=2)
        response = render(request, 'Notebooks/block1.html', {'terms': terms, 'block_range':block_range, 'block_obj': block_obj, 'page': page, 'form': form, 'notebook': notebook_id })
        return response

def partial_page(request, **kwargs):
    block = request.GET.get('block')
    return render(request, 'partials/showpage.html', {'block': block})

def editfield(request):
    page_id = request.GET.get('page')
    page = Scan.objects.get(pk=page_id)
    field = request.GET.get('field')
    data = {'page': page, 'field': field}
    result = render(request, 'partials/editfield.html', data)
    return result

def showfield(request):
    page_id = request.GET.get('page')
    page = Scan.objects.get(pk=page_id)
    field = request.GET.get('field')
    data = {'page': page, 'field': field}
    return render(request, 'partials/showfield.html', data)

def savefield(request):
    page_id = request.GET.get('page')
    page = Scan.objects.get(pk=page_id)
    field = request.GET.get('field')
    value = request.POST.get(field)
    save = request.GET.get('save')
    if save == "Yes" and value != None and getattr(page, field) != value:
        setattr(page, field, value)
        page.save()
    data = {'page': page, 'field': field}
    return render(request, 'partials/showfield.html', data)


def logout_view(request):
    logout(request)
    return redirect('/')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # Redirect to the home page after successful login
        else:
             return render(request, 'registration/login.html', {'error': 'Invalid credentials'}) # Render login page with error message
    # GET branch
    form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form}) # Render login page for GET requests

def home(request):
    request.session['filter'] = []
    books = Notebook.objects.all().order_by('name')
    return render(request, 'Notebooks/home.html', {'notebooks': books})

class TagAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = Tag.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

    def get_create_option(self, context, q):
        return []

def TagPost(request):
    scan_id = request.POST.get('scan_id')
    scan = Scan.objects.get(pk=int(scan_id))
    tags = []
    if 'remove' in request.POST:
        to_remove = request.POST.getlist('remove')
        tags = list(scan.tags.values_list('name', flat=True))
        for tag in to_remove:
            tags.remove(tag)
    elif 'clear' in request.POST:
        tags=[]
    else:
        tags = request.POST.getlist('tags[]')        
    scan.tags.set(tags, clear=True)
    scan.save()
    return HttpResponse()