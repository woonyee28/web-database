from django.db import models

class Enhancer(models.Model):
    enhancerID = models.AutoField(primary_key=True)
    enhancerName = models.CharField(max_length=255)
    chromosomeNumberAsReported = models.IntegerField()
    startAsReported = models.IntegerField()
    endAsReported = models.IntegerField()
    genomeAssemblyAsReported = models.CharField(max_length=255)
    organism = models.CharField(max_length=255)
    hg38Chromosome = models.IntegerField()
    hg38Start = models.IntegerField()
    hg38End = models.IntegerField()

    class Meta:
        unique_together = (('enhancerName', 'chromosomeNumberAsReported', 'startAsReported', 'endAsReported', 'genomeAssemblyAsReported'),)
        managed = False
        db_table = 'enhancers'

class Target(models.Model):
    targetID = models.AutoField(primary_key=True)
    geneName = models.CharField(max_length=255)
    geneID = models.IntegerField()
    organ = models.CharField(max_length=255)
    tissue = models.CharField(max_length=255)
    cell = models.CharField(max_length=255)

    class Meta:
        unique_together = (('geneName', 'geneID', 'organ', 'tissue', 'cell'),)
        managed = False  
        db_table = 'targets'

class Evidence(models.Model):
    evidenceID = models.AutoField(primary_key=True)
    functionalYN = models.CharField(max_length=3)  # Assuming "Y/N" or similar short text
    methodAssay = models.CharField(max_length=255)
    relevantText = models.TextField()
    page = models.IntegerField()
    title = models.CharField(max_length=255)
    firstAuthor = models.CharField(max_length=255)
    pubYear = models.IntegerField()
    journal = models.CharField(max_length=255)
    volumePageNumber = models.CharField(max_length=255)
    doi = models.CharField(max_length=255)
    pmid = models.IntegerField()
    curator = models.CharField(max_length=255)
    date = models.DateField()
    comments = models.TextField()

    class Meta:
        unique_together = (('relevantText', 'pmid', 'comments', 'methodAssay', 'functionalYN'),)
        managed = False 
        db_table = 'evidence'


class Activity(models.Model):
    activityID = models.AutoField(primary_key=True)
    evidenceID = models.ForeignKey(Evidence, on_delete=models.CASCADE, db_column='evidenceID')
    targetID = models.ForeignKey(Target, on_delete=models.CASCADE, db_column='targetID')
    enhancerID = models.ForeignKey(Enhancer, on_delete=models.CASCADE, db_column='enhancerID')

    class Meta:
        managed = False 
        db_table = 'activity'

