from django.test import TestCase

from experiments.models import Slot
from experiments.populate.measurement import MeasurementsPopulator, MeasurementsPrerequisitesPopulator, MAX_SLOTS


class MeasurementTest(TestCase):

    def setUp(self) -> None:
        MeasurementsPrerequisitesPopulator.populate_all_prerequisites()

    def test_has_slide_number(self):
        m = MeasurementsPopulator.create_automated_measurement_with_multiple_slots()
        self.assertTrue(m.has_slide_number(1))
        self.assertTrue(m.has_slide_number(MAX_SLOTS))
        self.assertFalse(m.has_slide_number(MAX_SLOTS + 1))
        Slot.objects.get(measurement=m,
                         automated_slide_num=1).delete()
        Slot.objects.get(measurement=m,
                         automated_slide_num=MAX_SLOTS).delete()
        self.assertFalse(m.has_slide_number(1))
        self.assertFalse(m.has_slide_number(MAX_SLOTS))