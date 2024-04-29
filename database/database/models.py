from django.db import models

class Enhancers2016(models.Model):
    id = models.IntegerField(db_column='id',primary_key=True)  # Add this line for the primary key
    enhancer_no = models.IntegerField(db_column='Enhancer No.')
    enhancer_name = models.TextField(db_column='Enhancer name')
    chromosome_number_as_reported = models.IntegerField(db_column='Chromosome number (as reported)')
    start_position_as_reported = models.IntegerField(db_column='Start Position (as reported)')
    end_position_as_reported = models.IntegerField(db_column='End Position (as reported)')
    genome_assembly_as_reported = models.TextField(db_column='Genome Assembly (as reported)')
    organism = models.TextField()
    hg38_chromosome = models.IntegerField(db_column='hg38 Chromosome')
    hg38_start = models.IntegerField(db_column='hg38 Start')
    hg38_end = models.IntegerField(db_column='hg38 End')
    target_gene = models.TextField(db_column='Target Gene')
    gene_id_target = models.IntegerField(db_column='Gene ID (Target)')
    organ = models.TextField()
    tissue = models.TextField()
    cell = models.TextField()
    functional_yn = models.TextField(db_column='Functional Y/N')
    method_assay = models.TextField(db_column='Method / Assay')
    relevant_text = models.TextField(db_column='Relevant Text')
    page_of_text = models.IntegerField(db_column='Page of Text')
    source_title = models.TextField(db_column='Source Title')
    source_author_first = models.TextField(db_column='Source Author (first Author only)')
    source_year_of_publication = models.IntegerField(db_column='Source Year of Publication')
    source_journal = models.TextField(db_column='Source Journal')
    source_volume_and_page_numbers = models.TextField(db_column='Source Volume and Page Numbers')
    doi = models.TextField()
    pmid = models.IntegerField()
    curator = models.TextField()
    date = models.TextField()
    comments = models.TextField()
    year = models.IntegerField(db_column='Sheet Name')

    class Meta:
        managed = False
        db_table = 'enhancers'  # Adjust the table name accordingly
