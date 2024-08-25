from django.shortcuts import render, get_object_or_404
from .models import Enhancer, Target, Activity, Evidence
from django.core.paginator import Paginator

def main_page_enhancer_view(request):
    search_type = request.GET.get('search_type')
    start = request.GET.get('start')
    end = request.GET.get('end')
    warning_message = None 
    
    data = Enhancer.objects.all()  # Retrieve all records initially
    
    if search_type == 'hg38':
        chromosome = request.GET.get('hg38_chromosome')
        start = request.GET.get('hg38_start')
        end = request.GET.get('hg38_end')
        
        if chromosome and start and end:
            try:
                start = int(start)
                end = int(end)
                
                if end - start > 1000000:
                    warning_message = "Warning: The difference between end and start positions must be less than 1 million."
                else:
                    data = data.filter(hg38Chromosome=chromosome, hg38Start=start, hg38End=end)
            except ValueError:
                warning_message = "Start and End positions must be valid integers."
        elif chromosome:
            data = data.filter(hg38Chromosome=chromosome)

    
    elif search_type == 'reported':
        organism = request.GET.get('organism')
        genome_assembly = request.GET.get('genome_assembly')
        chromosome_number = request.GET.get('chromosome_number')
        start = request.GET.get('start')
        end = request.GET.get('end')
        
        if organism and genome_assembly and chromosome_number and start and end:
            try:
                start = int(start)
                end = int(end)
                
                if end - start > 1000000:
                    warning_message = "Warning: The difference between end and start positions must be less than 1 million."
                else:
                    data = data.filter(
                        organism=organism,
                        genomeAssemblyAsReported=genome_assembly,
                        chromosomeNumberAsReported=chromosome_number,
                        startAsReported__gte=start,
                        endAsReported__lte=end
                    )
            except ValueError:
                warning_message = "Start and End positions must be valid integers."

    elif search_type == 'target':
        target_gene = request.GET.get('target_gene')
        organ = request.GET.get('organ')
        tissue = request.GET.get('tissue')
        cell = request.GET.get('cell')
        
        if target_gene or organ or tissue or cell:
            # Filter targets based on the search criteria
            targets = Target.objects.all()
            
            if target_gene:
                targets = targets.filter(geneID__icontains=target_gene)
            if organ:
                targets = targets.filter(organ__icontains=organ)
            if tissue:
                targets = targets.filter(tissue__icontains=tissue)
            if cell:
                targets = targets.filter(cell__icontains=cell)
            
            # Get the IDs of the matching targets
            target_ids = targets.values_list('targetID', flat=True)
            
            # Find all activities related to the matching targets
            activities = Activity.objects.filter(targetID__in=target_ids)
            
            # Get the IDs of the related enhancers
            enhancer_ids = activities.values_list('enhancerID', flat=True)
            
            # Filter enhancers based on the related enhancer IDs
            data = data.filter(enhancerID__in=enhancer_ids)

    # Pagination for Enhancer data
    items_per_page = 30
    paginator = Paginator(data, items_per_page)
    page_number = request.GET.get('page', 1)
    page_data = paginator.get_page(page_number)

    return render(request, 'index.html', {
        'page_data': page_data,
        'warning_message': warning_message
    })

def enhancer_detail_view(request, id):
    enhancer = get_object_or_404(Enhancer, enhancerID=id)

    activities = Activity.objects.filter(enhancerID=enhancer.enhancerID)

    target_ids = activities.values_list('targetID', flat=True)
    evidence_ids = activities.values_list('evidenceID', flat=True)

    target_data = Target.objects.filter(targetID__in=target_ids)
    evidence_data = Evidence.objects.filter(evidenceID__in=evidence_ids)

    return render(request, 'enhancer_detail.html', {
        'item': enhancer,
        'target_data': target_data,
        'evidence_data': evidence_data,
    })
