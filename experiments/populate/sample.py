from experiments.models import Tissue, Age, Background, Genotype, Sample


class SamplesPopulator:

    def populate_tissues(self):
        Tissue.objects.get_or_create(name="Kidney")[0].save()
        Tissue.objects.get_or_create(name="Adrenal gland")[0].save()

    def populate_ages(self):
        Age.objects.get_or_create(name="GA 8.2")[0].save()
        Age.objects.get_or_create(name="Fetal")[0].save()

    def populate_backgrounds(self):
        Background.objects.get_or_create(name="Unknown")[0].save()

    def populate_genotypes(self):
        Genotype.objects.get_or_create(name="Unknown")[0].save()

    def populate_samples(self):
        self.populate_tissues()
        t1 = Tissue.objects.get(name="Kidney")
        t2 = Tissue.objects.get(name="Adrenal gland")
        b = Background.objects.first()
        g = Genotype.objects.first()
        a1 = Age.objects.first()
        a2 = Age.objects.last()
        s1 = Sample.objects.get_or_create(name="L14-KID-0-FFPE-1-S3i",
                                          species=1,
                                          age=a1,
                                          genotype=g,
                                          background=b,
                                          tissue=t1)
        s2 = Sample.objects.get_or_create(name="L14-ADR-0-FFPE-1-S3i",
                                          species=2,
                                          age=a2,
                                          genotype=g,
                                          background=b,
                                          tissue=t2)
