import datetime
from typing import List, Union, Dict

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models

from experiments.constants import *
from experiments.helpers import is_empty
from experiments.models import ChannelTarget, Researcher, Measurement, \
    MeasurementNumber, MagBinOverlap, Project, Channel, Target, AutomatedSlide, Technology, LowMagReference, Plate
from experiments.models.slide import Section
from experiments.xls import MODELS_MAPPING
from experiments.xls.date_parsers import DateParser
from experiments.xls.slides_importer import SamplesImporter, SlidesImporter


class XLSRowParser:
    """A class to implement parsing a Measurement object and related objects from a Pandas row."""

    def __init__(self, row: Dict):
        self.row = row

    @staticmethod
    def _parse_section_numbers_string(sections_string: str) -> List[int]:
        """
        :param sections_string: a string in a format "<number>[, <number>, ..]"
        :return: a list of numbers
        """
        if type(sections_string) is not str:
            sections_string = str(sections_string)
        try:
            return list(map(lambda s: int(float(s)), sections_string.split(",")))
        except ValueError:
            raise ValidationError("The sections string must be whole comma-separated numbers, e.g. '1,2,3' ")

    def parse_section_numbers(self) -> List[int]:
        return self._parse_section_numbers_string(self.row[SECTION_NUM])

    def parse_sections(self) -> List[Section]:
        SamplesImporter(self.row).import_samples()
        slide = SlidesImporter(self.row).import_slide()
        return slide.section_set.all()

    def parse_channel_targets(self) -> List[ChannelTarget]:
        """Get or create ChannelTarget objects from a row."""
        result = []
        for i in range(1, MAX_CHANNELS + 1):
            channel_column = CHANNEL + f"{i}"
            target_column = TARGET + f"{i}"
            channel_name = self.row.get(channel_column)
            target_name = self.row.get(target_column)
            if bool(channel_name) != bool(target_name):
                raise ValueError("Channel and target must be present together, "
                                 f"problematic columns are: {channel_column}, {target_column}")
            if channel_name and target_name:
                channel = Channel.objects.get_or_create(name=channel_name)[0]
                target = Target.objects.get_or_create(name=target_name)[0]
                cht = ChannelTarget.objects.get_or_create(channel=channel, target=target)[0]
                result.append(cht)
        return result

    def _get_or_create_model_instance(self, column: str, value: str) -> Union[models.Model, None]:
        try:
            return MODELS_MAPPING[column](value)
        except KeyError:
            raise NotImplementedError(f"Column {column} is not mapped to a processing function")

    @staticmethod
    def _handle_empty_value(column_name: str) -> None:
        if column_name in REQUIRED_COLUMNS:
            raise ValueError(f"Required column is empty: {column_name}")
        else:
            return None

    def _parse_column(self, column: str) -> Union[models.Model, None]:
        value = self.row.get(column, '')
        if is_empty(value):
            return self._handle_empty_value(column)
        return self._get_or_create_model_instance(column, value)

    def parse_harmony_copy_deleted(self) -> bool:
        return self.row.get(HARMONY_COPY) == 'Yes'

    def parse_researcher(self) -> Researcher:
        return self._parse_column(RESEARCHER)

    def parse_project(self) -> Project:
        return self._parse_column(PROJECT)

    def parse_automated_slide(self) -> AutomatedSlide:
        return self._parse_column(SLIDE_ID)

    def parse_measurement_number(self) -> MeasurementNumber:
        return self._parse_column(MEASUREMENT_NUMBER)

    def parse_image_cycle(self) -> int:
        return self.row[IMAGE_CYCLE]

    def parse_mag_bin_overlap(self) -> MagBinOverlap:
        return self._parse_column(MAG_BIN_OVERLAP)

    def parse_technology(self) -> Technology:
        return self._parse_column(TECHNOLOGY)

    def parse_zplanes(self) -> ZPLANES:
        return self._parse_column(ZPLANES)

    def parse_location(self, location_column) -> Union[models.Model, None]:
        if location_column in {EXPORT_LOCATION, ARCHIVE_LOCATION, TEAM_DIR}:
            return self._parse_column(location_column)
        else:
            raise ValueError(f"Invalid location column: {location_column}")

    def parse_low_mag_reference(self) -> LowMagReference:
        return self._parse_column(LOW_MAG_REFERENCE)

    def parse_plate(self) -> Plate:
        return self._parse_column(AUTOMATED_PLATEID)

    def parse_text_column(self, text_column):
        if text_column in {NOTES_1, NOTES_2, POST_STAIN}:
            return self.row.get(text_column)
        else:
            raise ValueError(f"Invalid location column: {text_column}")

    def parse_automated_slide_num(self) -> int:
        sliden = self.row.get(AUTOMATED_SLIDEN)
        if not is_empty(sliden):
            return int(sliden)
        else:
            return 1

    def parse_date(self) -> datetime.date:
        return DateParser.parse_date(self.row[DATE])

    def get_measurement(self) -> Measurement:
        try:
            researcher = self.parse_researcher()
            image_cycle = self.parse_image_cycle()
            mag_bin_overlap = self.parse_mag_bin_overlap()
            project = self.parse_project()
            measurement = self.parse_measurement_number()
            date = self.parse_date()
            technology = self.parse_technology()
            low_mag_ref = self.parse_low_mag_reference()
            z_planes = self.parse_zplanes()
            automated_plate_id = self.parse_plate()
            notes1 = self.parse_text_column(NOTES_1)
            notes2 = self.parse_text_column(NOTES_2)
            exp_location = self.parse_location(EXPORT_LOCATION)
            arch_location = self.parse_location(ARCHIVE_LOCATION)
            team_dir = self.parse_location(TEAM_DIR)
            harmony_copy_deleted = self.parse_harmony_copy_deleted()
            post_stain = self.parse_text_column(POST_STAIN)
        except KeyError as e:
            raise ValidationError(f"A required column is absent: {e}")
        except (ValidationError, ObjectDoesNotExist) as e:
            raise ValueError(f"{e}")

        return Measurement(researcher=researcher,
                           project=project,
                           technology=technology,
                           plate=automated_plate_id,
                           mag_bin_overlap=mag_bin_overlap,
                           low_mag_reference=low_mag_ref,
                           post_stain=post_stain,
                           harmony_copy_deleted=harmony_copy_deleted,
                           notes_1=notes1,
                           notes_2=notes2,
                           export_location=exp_location,
                           archive_location=arch_location,
                           team_directory=team_dir,
                           measurement_number=measurement,
                           date=date,
                           image_cycle=image_cycle,
                           z_planes=z_planes)
