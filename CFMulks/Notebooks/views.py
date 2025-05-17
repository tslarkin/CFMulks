from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from .models import Notebook, Scan
from django.views.generic import View, ListView
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from roman import toRoman

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

class ScanListView(ListView):
    paginate_by = 5
    model = Scan
    ordering = ["file"]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        pages = self.get_queryset()
        paginator = Paginator(pages, self.paginate_by)
        page_no = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_no)
        context['page_obj'] = page_obj
        context['paginator_range'] = paginator.get_elided_page_range(number=page_no, on_each_side=1, on_ends=2)
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
                anchor = scan.file
                transcription = request.POST.get("transcription")
                description = request.POST.get("description")
                seq_num = request.POST.get("seq_num")
                scan.seq_num = seq_num
                scan.transcription = transcription
                scan.description = description
                scan.save()
                return HttpResponseRedirect("#"+anchor)
            page_number = request.POST.get("page_num", 1)
            target = "/scan/"+"?page="+str(page_number)
            return redirect(target)
        return HttpResponse()