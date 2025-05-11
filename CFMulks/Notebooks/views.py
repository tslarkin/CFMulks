from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from .models import Notebook, Scan
from django.views.generic import ListView
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect


def pages(request):
    all = Scan.objects.all().order_by('name')
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

class ScanListView(ListView):
    paginate_by = 5
    model = Scan

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        scan: Scan = context['page_obj']
        context['paginator_range'] = scan.paginator.get_elided_page_range(number=scan.number, on_each_side=1, on_ends=2)
        return context
    
    def get_queryset(self):
        return super().get_queryset().order_by('file')
    
    def post(self, request):
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