
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "image_tracking.settings")
django.setup()
from experiments.models import *


def save(arr):
    for a in arr:
        a.save()


class Populator:

    def populate_cellgen_project(self):
        CellGenProject.objects.create(key="ML_HEA").save()

    def populate_team_dirs(self):
        TeamDirectory.objects.create(name="t283_imaging").save()

    def populate_channels(self):
        ch1 = Channel.objects.create(name="Atto 425")
        ch2 = Channel.objects.create(name="Opal 520")
        save({ch1, ch2})

    def populate_targets(self):
        t1 = Target.objects.create(name="MYH11")
        t2 = Target.objects.create(name="dapB")
        t3 = Target.objects.create(name="POLR2A")
        t4 = Target.objects.create(name="BNC1")
        t5 = Target.objects.create(name="TTN")
        t6 = Target.objects.create(name="KCNJ8")
        t7 = Target.objects.create(name="ACKR1")
        save({t1, t2, t3, t4, t5, t6, t7})

    def populate_channel_target_pairs(self):
        self.populate_channels()
        self.populate_targets()
        ch1 = Channel.objects.get(name="Atto 425")
        ch2 = Channel.objects.get(name="Opal 520")

        t1 = Target.objects.get(name="MYH11")
        t2 = Target.objects.get(name="dapB")
        t3 = Target.objects.get(name="POLR2A")
        cht1 = ChannelTarget.objects.create(channel=ch1, target=t1)
        cht2 = ChannelTarget.objects.create(channel=ch1, target=t2)
        cht3 = ChannelTarget.objects.create(channel=ch1, target=t3)
        cht4 = ChannelTarget.objects.create(channel=ch2, target=t1)
        cht5 = ChannelTarget.objects.create(channel=ch2, target=t2)
        cht6 = ChannelTarget.objects.create(channel=ch2, target=t3)
        save({cht1, cht2, cht3, cht4, cht5, cht6})

    def populate_samples(self):
        s1 = Sample.objects.create(id="L14-KID-0-FFPE-1-S3i",
                                   species="human",
                                   age="Adult",
                                   genotype="Unknown",
                                   background="Unknown",
                                   tissue="Kidney")
        s2 = Sample.objects.create(id="L14-ADR-0-FFPE-1-S3i",
                                   species="human",
                                   age="Adult",
                                   genotype="Unknown",
                                   background="Unknown",
                                   tissue="Adrenal gland")
        save({s1, s2})

    def populate_slides(self):
        s1 = Slide.objects.create(automated_id="ML_HEA_007Q", barcode_id="S000000729")
        s2 = Slide.objects.create(automated_id="ML_HEA_007R", barcode_id="S000000724")
        s3 = Slide.objects.create(automated_id="ML_HEA_007S", barcode_id="S000000725")
        s4 = Slide.objects.create(automated_id="ML_HEA_007P", barcode_id="S000000726")
        save({s1, s2, s3, s4})

    def populate_sections(self):
        s1 = Sample.objects.get(id="L14-KID-0-FFPE-1-S3i")
        s2 = Sample.objects.get(id="L14-ADR-0-FFPE-1-S3i")
        sl1 = Slide.objects.get(automated_id="ML_HEA_007Q", barcode_id="S000000729")
        sl2 = Slide.objects.get(automated_id="ML_HEA_007R", barcode_id="S000000724")
        sc11 = Section.objects.create(number=1, sample=s1, slide=sl1)
        sc12 = Section.objects.create(number=2, sample=s1, slide=sl1)
        sc13 = Section.objects.create(number=3, sample=s1, slide=sl1)
        sc21 = Section.objects.create(number=1, sample=s2, slide=sl2)
        sc22 = Section.objects.create(number=2, sample=s2, slide=sl2)
        save({sc11, sc12, sc13, sc21, sc22})



    def populate_all(self):
        self.populate_cellgen_project()
        self.populate_team_dirs()
        self.populate_samples()
        self.populate_slides()
        self.populate_channel_target_pairs()
        self.populate_sections()

if __name__ == "__main__":
    p = Populator()
    p.populate_all()
