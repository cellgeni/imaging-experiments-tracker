from django.db import models


class NameModel(models.Model):
    name = models.CharField(max_length=40, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Path(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
