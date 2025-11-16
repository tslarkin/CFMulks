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
    page_set = "-".join(str(record.id) for record in records)
    filter = list(records.values_list('id', flat=True))
    request.session['filter'] = filter
    hints = []
    for record in records:
        transcription_hints = get_hints('transcription', terms, page_set, record)
        hints+= transcription_hints
#        description_hints = get_notes('description', terms, page_set,  record)
        
#        hints += description_hints
        hints += ['<div class="row" style="height: 30px"></div>']
    if len(hints) == 0:
        hints.append('<div class="row" style="text-align: center">No Matches Found</div>')
    return render(request, "partials/searchresults.html", {'hints': hints})

def get_hints(field_name, terms, page_set, record):
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
            url = f"/show_page_set/{record.id}/"
            hint = f'<a class="row" style="color:black; text-decoration:none;" href="{url}">'\
                +f'<div class="cell label {field_name}">{label}</div>'\
                +f'<div class="cell {field_name}">{prefix}' + field[a:spanstart] + '<u>'+text+'</u>' + field[spanend:b] + suffix+'</div>'\
                +'</a>'
            hint = mark_safe(hint)
            hints.append(hint)
    return hints

def get_notes(field_name, terms, page_set, record):
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
   
def show_page(request, **kwargs):
    pageid = kwargs['pageid']
    # Leaving the old model name unchanged
    page = Scan.objects.get(pk=pageid)
    pages = request.GET.get('pages')
    if pages == None:
        return render(request, 'Notebooks/page.html', {'page':page})            
    else:
        numbers = [int(x) for x in pages.split('-')]
        pages = [Scan.objects.get(pk=n) for n in numbers].order_by('file')
        paginator = Paginator(pages,1)
        block_obj = paginator.get_page(page)
        return render(request, 'Notebooks/page.html', {'page':page, 'block_obj': block_obj})

def show_page_set(request, focus_id):
    is_page_number = focus_id[0] == 'P'
    if is_page_number:
        focus_id = focus_id[1:]
    focus_id = int(focus_id)
    numbers = request.session['filter']
    pageset = Scan.objects.filter(pk__in=numbers).order_by('file')
    paginator = Paginator(pageset,1)
    index = focus_id if is_page_number else numbers.index(focus_id)+1
    block_obj = paginator.get_page(index)
    response = render(request, 'Notebooks/page.html', {'block_obj': block_obj})
    #response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

def partial_page(request, **kwargs):
    block = request.GET.get('block')
    return render(request, 'partials/showpage.html', {'block': block})

def editfield(request):
    page_id = request.GET.get('page')
    page = Scan.objects.get(pk=page_id)
    field = request.GET.get('field')
    data = {'page': page, 'field': field}
    return render(request, 'partials/editfield.html', data)

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
    books = Notebook.objects.all().order_by('name')
    return render(request, 'Notebooks/home.html', {'notebooks': books})

def show___scan(request, **kwargs):
    scanid = kwargs['scanid']
    scan = Scan.objects.get(pk=scanid)
    pages = request.GET.get('pages').split(",")
    numbers = [int(x) for x in pages]
    paginator = Paginator(numbers,1)
    page_obj = paginator.get_page(scanid)
    return render(request, 'Notebooks/scan.html', {'scan':scan, 'page_obj': page_obj})

class BlockView(ListView):
    paginate_by = 5
    model = Scan
    ordering = ["file"]
    template_name = "Notebooks/block.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        pages = self.get_queryset()
        paginator = Paginator(pages, self.paginate_by)
        block_no = self.request.GET.get('block', 1)
        block_obj = paginator.get_page(block_no)
        context['block_obj'] = block_obj
        context['block_range'] = paginator.get_elided_page_range(number=block_no, on_each_side=3, on_ends=2)
        return context
    
    def get_queryset(self):
        notebook_id = self.kwargs['notebook_id']
        qs = super().get_queryset().filter(notebook__id=notebook_id)
        return qs
    
    def post(self, request, **kwargs):
        if request.method == 'POST':
            form_type = request.POST.get('form_type')
            # form_type is either 'scan_update' or 'jump'
            # In the first case, POST.page_num is the current page. Need to update the ORM.
            # In the second case, POST.page_num is the page to jump to. Just jump
            if form_type == 'scan_update':
                scan_id = request.POST.get("id")
                scan = Scan.objects.get(pk=int(scan_id))
                anchor = scan.name()
                transcription = request.POST.get("transcription")
                description = request.POST.get("description")
                seq_num = request.POST.get("seq_num")
                scan.seq_num = seq_num
                scan.transcription = transcription
                scan.description = description
                scan.save()
                return HttpResponseRedirect("#"+anchor)
            block_number = request.POST.get("block_num", 1)
            notebook_id = self.kwargs['notebook_id']
            target = "/block/"+str(notebook_id)+"/?block="+str(block_number)
            return redirect(target)
        return HttpResponse()