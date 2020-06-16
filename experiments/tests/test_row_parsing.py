import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from experiments import helpers
from experiments.constants import *
from experiments.models import Channel
from experiments.populate.measurement import MeasurementsPrerequisitesPopulator
from experiments.xls.date_parsers import DateParser
from experiments.xls.row_parser import XLSRowParser


class XLSMeasurementsParserTestCase(TestCase):
    """
    Test whether fields in a row that represent a measurement_number in a spreadsheet
    properly map to corresponding Measurement attributes.
    """

    def setUp(self) -> None:
        MeasurementsPrerequisitesPopulator.populate_all_prerequisites()

    def test_parse_sections(self):
        # TODO: check section number correspond to samples
        pass

    def test_parse_channel_targets(self):
        # TODO: test if channel and target are not present together
        # TODO: validation on spreadsheet level if channel and target columns are not present together
        def get_or_create_channel(name: str) -> str:
            return str(Channel.objects.get_or_create(name=name)[0])

        row = {
            CHANNEL1: get_or_create_channel("ch1"),
            TARGET1: "t1",
            CHANNEL2: get_or_create_channel("ch1"),
            TARGET2: "t2",
            CHANNEL3: get_or_create_channel("ch3"),
            TARGET3: "t1",
            CHANNEL4: get_or_create_channel("ch4"),
            TARGET4: "t4",
            CHANNEL5: get_or_create_channel("ch5"),
            TARGET5: "t5",
            CHANNEL6: get_or_create_channel("ch6"),
            TARGET6: "t6",
            CHANNEL7: get_or_create_channel("ch7"),
            TARGET7: "t7",
        }
        mpp = XLSRowParser(row)
        channel_targets = mpp.parse_channel_targets()
        for i in range(1, MAX_CHANNELS + 1):
            self.assertEqual(row[helpers.get_channel_column_name(i)], channel_targets[i - 1].channel.name)
            self.assertEqual(row[helpers.get_target_column_name(i)], channel_targets[i - 1].target.name)

    def test_parse_section_numbers(self):
        self.assertEqual([1, 2, 3], XLSRowParser._parse_section_numbers_string("1,2,3"))
        self.assertEqual([1, 2, 3], XLSRowParser._parse_section_numbers_string("1, 2, 3"))
        self.assertEqual([1, 2, 3], XLSRowParser._parse_section_numbers_string("1 , 2 ,3"))
        self.assertEqual([1], XLSRowParser._parse_section_numbers_string("1"))
        self.assertEqual([1, 2], XLSRowParser._parse_section_numbers_string("1.0, 2.0"))
        self.assertEqual([1], XLSRowParser._parse_section_numbers_string(1))
        self.assertEqual([1], XLSRowParser._parse_section_numbers_string(float(1.0)))
        with self.assertRaises(ValidationError):
            XLSRowParser._parse_section_numbers_string("cat, dog, 2")

    def test_parse_date(self):
        year = 2019
        month = 2
        day = 2
        sample_date = datetime.date(year, month, day)
        self.assertEqual(sample_date, DateParser.parse_date(f"{day}.{month}.{year}"))
        self.assertEqual(sample_date, DateParser.parse_date(f"0{day}/0{month}/{year}"))
        self.assertEqual(sample_date, DateParser.parse_date(f"0{day}-0{month}-{year}"))
        self.assertEqual(sample_date, DateParser.parse_date(datetime.date(month=month, year=year, day=day)))
        self.assertEqual(sample_date, DateParser.parse_date(datetime.datetime(month=month, year=year, day=day)))
        wrong_dates = ["1.13.2018", "some word", "1 02 2019", "2019.12.3", '0.0', 0.0, 0]
        for wrong_date in wrong_dates:
            with self.assertRaises(ValueError):
                DateParser.parse_date(wrong_date)
