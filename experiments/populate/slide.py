from experiments.models import Slide, SlideBarcode, Sample, Section, Slot
from experiments.populate.sample import SamplesPopulator


class SlidesPopulator:
    same_barcode = "S000000726"

    @staticmethod
    def create_n_slides_with_the_same_barcode(barcode: SlideBarcode, n: int) -> None:
        """Create a given number of slides with the same barcode."""
        same_slides = Slide.objects.filter(barcode=barcode)
        for i in range(len(same_slides), n + 1):
            Slide.objects.create(barcode=barcode)

    @classmethod
    def populate_slides(cls):
        b1 = SlideBarcode.objects.get_or_create(name="S000000724")[0]
        b2 = SlideBarcode.objects.get_or_create(name="S000000725")[0]
        b3 = SlideBarcode.objects.get_or_create(name=cls.same_barcode)[0]
        s2 = Slide.objects.get_or_create(barcode=b1)
        s3 = Slide.objects.get_or_create(barcode=b2)
        cls.create_n_slides_with_the_same_barcode(b3, 2)

    @classmethod
    def populate_sections(cls):
        sp = SamplesPopulator()
        sp.populate_samples()
        cls.populate_slides()
        s1 = Sample.objects.get(name="L14-KID-0-FFPE-1-S3i")
        s2 = Sample.objects.get(name="L14-ADR-0-FFPE-1-S3i")
        sl1 = Slide.objects.get(barcode__name="S000000724")
        sl2 = Slide.objects.get(barcode__name="S000000725")
        sc11 = Section.objects.get_or_create(number=1, sample=s1, slide=sl1)
        sc12 = Section.objects.get_or_create(number=2, sample=s1, slide=sl1)
        sc13 = Section.objects.get_or_create(number=3, sample=s1, slide=sl1)
        sc21 = Section.objects.get_or_create(number=1, sample=s2, slide=sl2)
        sc22 = Section.objects.get_or_create(number=2, sample=s2, slide=sl2)

    @classmethod
    def populate_all(cls):
        cls.populate_slides()
        cls.populate_sections()
