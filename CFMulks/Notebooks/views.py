from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Notebook, Page

def pages(request):
    all = Page.objects.all().order_by('name')
    paginator = Paginator(all, 1)
    page_num = int(request.GET.get('page', 1))
    page_num = max(page_num, 1)
    page_num = min(page_num, paginator.num_pages)
    page = paginator.page(page_num)
    data = {
        'page': page.object_list[0],
        'page_num': page.number,
    }
    return render(request, 'page.html', data)
