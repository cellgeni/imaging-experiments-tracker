from django.db import models


class Tissue(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Sample(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    species = models.IntegerField(blank=True, null=True, choices=[
        (1, 'Hca'),
        (2, 'Mmu')
    ])
    age = models.CharField(max_length=20, blank=True, null=True)
    genotype = models.CharField(max_length=20, null=True, blank=True)
    background = models.CharField(max_length=20, null=True, blank=True)
    tissue = models.ForeignKey(Tissue, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.id