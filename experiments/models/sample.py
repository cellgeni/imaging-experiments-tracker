from django.db import models

from experiments.models.base import NameModel


class Tissue(NameModel):
    pass


class Age(NameModel):
    pass


class Genotype(NameModel):
    pass


class Background(NameModel):
    name = models.CharField(max_length=100)


class Sample(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    species = models.IntegerField(blank=True, null=True, choices=[
        (1, 'Hca'),
        (2, 'Mmu')
    ])
    age = models.ForeignKey(Age, on_delete=models.SET_NULL, blank=True, null=True)
    genotype = models.ForeignKey(Genotype, on_delete=models.SET_NULL, null=True, blank=True)
    background = models.ForeignKey(Background, on_delete=models.SET_NULL, null=True, blank=True)
    tissue = models.ForeignKey(Tissue, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.id
