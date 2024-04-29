from django.shortcuts import render, get_object_or_404
from .models import Enhancers2016
from django.core.paginator import Paginator


def main_page_view(request):
    search_query = request.GET.get('q')
    year_filter = request.GET.get('year')
    
    data = Enhancers2016.objects.all()  # Retrieve all records initially
    
    if search_query:
        data = data.filter(enhancer_name__icontains=search_query)
    
    if year_filter:
        data = data.filter(year=int(year_filter))
    
    # Pagination
    items_per_page = 30
    paginator = Paginator(data, items_per_page)
    page_number = request.GET.get('page', 1)
    page_data = paginator.get_page(page_number)

    return render(request, 'index.html', {'page_data': page_data})



def enhancer_detail_view(request, id):
    enhancer = get_object_or_404(Enhancers2016, id=id)
    return render(request, 'enhancer_detail.html', {'item': enhancer})

