from django.test import TestCase

# Create your tests here.
from .models import *
from .populate import *


class AnimalTestCase(TestCase):
    def setUp(self):
        Populator.populate_all()

    def test_populator(self):
        """Animals that can speak are correctly identified"""
        lion = Animal.objects.get(name="lion")
        cat = Animal.objects.get(name="cat")
        self.assertEqual(lion.speak(), 'The lion says "roar"')
        self.assertEqual(cat.speak(), 'The cat says "meow"')