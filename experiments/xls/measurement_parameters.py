import datetime
from typing import List, Set, Tuple
from uuid import UUID

import pandas as pd
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from experiments.constants import SLIDE_BARCODE, SECTIONS, CHANNEL_TARGET, UUID, RESEARCHER, TECHNOLOGY, IMAGE_CYCLE, \
    DATE, \
    MEASUREMENT, LOW_MAG_REFERENCE, AUTOMATED_PLATEID, AUTOMATED_SLIDEN, MAG_BIN_OVERLAP, NOTES_1, NOTES_2, ZPLANES, \
    EXPORT_LOCATION, ARCHIVE_LOCATION, TEAM_DIR
from experiments.models import Section, Slide, ChannelTarget, Researcher, Technology, TeamDirectory, Measurement
from experiments.xls import xls_logger as logger

class MeasurementM2MFields:

    def __init__(self, channel_target_pairs: Set[ChannelTarget],
                 sections: Set[Section]):
        self.channel_target_pairs = channel_target_pairs
        self.sections = sections


class MeasurementParameters:

    def __init__(self, model: Measurement, m2m_fields: MeasurementM2MFields):
        self.model = model
        self.m2m_fields = m2m_fields

    def _create_sections(self) -> None:
        for section in self.m2m_fields.sections:
            self.model.sections.add(section)

    def _create_channel_target_pairs(self) -> None:
        for chtp in self.m2m_fields.channel_target_pairs:
            self.model.channel_target_pairs.add(chtp)

    def _create_m2m_fields(self) -> None:
        self._create_sections()
        self._create_channel_target_pairs()

    def create_db_object(self) -> UUID:
        self.model.save()
        self._create_m2m_fields()
        return self.model.uuid

    def validate_current_model(self):
        try:
            # we don't validate uniqueness since a record with the same uuid can be updated
            # and we don't have custom validation for now
            # https://docs.djangoproject.com/en/3.0/ref/models/instances/#validating-objects
            self.model.clean_fields()
        except ValidationError as e:
            logger.error(e)
            raise ValueError(f"Some fields are invalid: {e}")

    def update_db_object(self) -> UUID:
        self.validate_current_model()
        existing_record = Measurement.objects.get(uuid=self.model.uuid)
        existing_record.delete()
        return self.create_db_object()

    def were_created(self) -> bool:
        m = Measurement.objects.get(uuid=self.model.uuid)
        return set(m.sections.all()) == self.m2m_fields.sections and \
               set(m.channel_target_pairs.all()) == self.m2m_fields.channel_target_pairs


class DateParser:

    def __init__(self, datestring: str):
        self.check_non_null_date(datestring)
        self.separator = self.get_separator(datestring)
        self.datestring = datestring

    def check_non_null_date(self, datestring: str) -> None:
        # Excel transforms null values into floats like 0.0
        if type(datestring) is not str:
            self.raise_value_error()

    @staticmethod
    def get_separator(datestring: str) -> str:
        if "." in datestring:
            return "."
        else:
            return "/"

    def raise_value_error(self):
        raise ValueError("Date must be in format DD.MM.YYYY or DD/MM/YYYY")

    def check_valid_year(self, year: int) -> None:
        if year < 2000:
            self.raise_value_error()

    def split_date(self) -> Tuple[int, int, int]:
        date_array = list(map(lambda x: int(x), self.datestring.split(self.separator)))
        self.check_valid_year(date_array[2])
        return date_array[2], date_array[1], date_array[0]

    def parse(self) -> datetime.date:
        try:
            year, month, day = self.split_date()
            return datetime.date(year, month, day)
        except (AttributeError, ValueError, IndexError):
            self.raise_value_error()


class MeasurementParametersParser:

    def __init__(self, row: pd.Series):
        self.row = row

    @staticmethod
    def _parse_section_numbers(sections_string: str) -> List[int]:
        """
        :param sections_string: a string in a format "<number>[, <number>, ..]"
        :return: a list of numbers
        """
        if type(sections_string) is not str:
            sections_string = str(sections_string)
        try:
            return list(map(lambda s: int(float(s)), sections_string.split(",")))
        except ValueError:
            raise ValueError("The sections string must be whole comma-separated numbers, e.g. '1,2,3' ")

    def _parse_sections(self) -> Set[Section]:
        sections = set()
        slide = Slide.get_slide(self.row[SLIDE_BARCODE])
        section_numbers = self._parse_section_numbers(self.row[SECTIONS])
        for num in section_numbers:
            section = Section.get_section(num, slide)
            sections.add(section)
        return sections

    def _parse_channel_targets(self) -> Set[ChannelTarget]:
        result = set()
        for i in range(1, 6):
            column = CHANNEL_TARGET + str(i)
            if not pd.isnull(self.row.get(column)):
                channel, target = ChannelTarget.get_channel_and_target_from_str(self.row[column])
                result.add(ChannelTarget.objects.get(channel__name=channel, target__name=target))
        return result

    @staticmethod
    def _parse_date(datestring):
        return DateParser(datestring).parse()

    def get_params(self) -> MeasurementParameters:
        try:
            uuid = self.row[UUID]
            researcher = Researcher.objects.get(employee_key=self.row[RESEARCHER])
            sections = self._parse_sections()
            technology = Technology.objects.get(name=self.row[TECHNOLOGY])
            image_cycle = self.row[IMAGE_CYCLE]
            channel_targets = self._parse_channel_targets()
            date = self._parse_date(self.row[DATE])
            measurement = self.row[MEASUREMENT]
            low_mag_ref = self.row[LOW_MAG_REFERENCE]
            automated_plate_id = self.row[AUTOMATED_PLATEID]
            automated_sliden = self.row[AUTOMATED_SLIDEN]
            mag_bin_overlap = self.row[MAG_BIN_OVERLAP]
            notes1 = self.row[NOTES_1]
            notes2 = self.row[NOTES_2]
            z_planes = self.row[ZPLANES]
            exp_location = self.row[EXPORT_LOCATION]
            arch_location = self.row[ARCHIVE_LOCATION]
            team_dir = TeamDirectory.objects.get(name=self.row[TEAM_DIR])
        except ObjectDoesNotExist as e:
            raise ValueError(f"{e}")
        model = Measurement(uuid=uuid,
                            researcher=researcher,
                            technology=technology,
                            automated_plate_id=automated_plate_id,
                            automated_slide_num=automated_sliden,
                            mag_bin_overlap=mag_bin_overlap,
                            notes_1=notes1,
                            notes_2=notes2,
                            export_location=exp_location,
                            archive_location=arch_location,
                            team_directory=team_dir,
                            low_mag_reference=low_mag_ref,
                            measurement=measurement,
                            date=date,
                            image_cycle=image_cycle,
                            z_planes=z_planes)
        m2mfields = MeasurementM2MFields(channel_targets, sections)
        return MeasurementParameters(model, m2mfields)
