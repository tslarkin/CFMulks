from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from .models import Notebook, Page
from django.views.generic import ListView
from django.http import JsonResponse, HttpResponse
from .forms import UpdatePage


def pages(request):
    all = Page.objects.all().order_by('name')
    paginator = Paginator(all, 3)
    page_num = int(request.GET.get('page', 1))
    page_num = max(page_num, 1)
    page_num = min(page_num, paginator.num_pages)
    page = paginator.page(page_num)
    data = {
        'page': page.object_list[0],
        'page_num': page.number,
    }
    return render(request, 'page.html', data)

class PageListView(ListView):
    paginate_by = 2
    model = Page

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        page: Page = context['page_obj']
        form = UpdatePage()
        context['form']=form
        context['paginator_range'] = page.paginator.get_elided_page_range(number=page.number, on_each_side=1, on_ends=2)
        return context
    
    def get_queryset(self):
        return super().get_queryset().order_by('name')
    
    def post(self, request):
        if request.method == 'POST':
            form_type = request.POST.get('form_type')
            if form_type == 'jump':
                page_number = request.POST.get("page_num", 1)
                target = "/pages/"+"?page="+str(page_number)
                return redirect(target)

        return HttpResponse()