from django.shortcuts import render, get_object_or_404
from .models import Enhancer, Target, Activity, Evidence
from django.core.paginator import Paginator


def main_page_enhancer_view(request):
    search_type = request.GET.get('search_type')
    target_clicked = request.GET.get('target_clicked')
    data = None
    enhancers = None
    target_info = None  # Variable to store geneID and geneName
    
    if search_type == 'hg38':
        data = Enhancer.objects.all()
        chromosome = request.GET.get('hg38_chromosome')
        
        if chromosome:
            data = data.filter(hg38Chromosome=chromosome)
    
    elif search_type == 'reported':
        data = Enhancer.objects.all()
        organism = request.GET.get('organism')
        chromosome_number = request.GET.get('chromosome_number')
        
        if organism and chromosome_number:
            data = data.filter(organism=organism, chromosomeNumberAsReported=chromosome_number)

    elif search_type == 'target':
        target_gene = request.GET.get('target_gene')
        data = Target.objects.all()
        
        if target_gene:
            target_gene = target_gene.lower()
            data = data.filter(geneName__istartswith=target_gene)
        
        # If a target is clicked, find related enhancers
        if target_clicked:
            targets = Target.objects.filter(geneID=target_clicked)
            
            # Store the geneID and geneName of the first matched target
            if targets.exists():
                target_info = {
                    'geneID': targets.first().geneID,
                    'geneName': targets.first().geneName
                }
            
            enhancer_ids = Activity.objects.filter(targetID__in=targets.values_list('targetID', flat=True)).values_list('enhancerID', flat=True)
            enhancers = Enhancer.objects.filter(enhancerID__in=enhancer_ids)
            
            if enhancers.exists():
                print("There are enhancers related to this target.")
            else:
                print("No enhancers found for this target.")
    
    return render(request, 'index.html', {
        'page_data': data,
        'enhancers': enhancers,
        'target_info': target_info,  # Pass the target info to the template
        'search_type': search_type,
        'target_clicked': target_clicked,
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
