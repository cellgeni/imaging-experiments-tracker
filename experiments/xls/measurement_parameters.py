from typing import List, Set, Union, Dict, Callable
from uuid import UUID

import pandas as pd
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from pandas._libs.tslibs.timestamps import Timestamp

from django.db import models
from experiments.constants import SLIDE_BARCODE, SECTION_NUM, CHANNEL_TARGET, UUID, RESEARCHER, TECHNOLOGY, IMAGE_CYCLE, \
    DATE, \
    MEASUREMENT, LOW_MAG_REFERENCE, AUTOMATED_PLATEID, AUTOMATED_SLIDEN, MAG_BIN_OVERLAP, NOTES_1, NOTES_2, ZPLANES, \
    EXPORT_LOCATION, ARCHIVE_LOCATION, TEAM_DIR, SLIDE_ID, TISSUE, BACKGROUND, GENOTYPE, AGE
from experiments.models import Section, Slide, ChannelTarget, Researcher, Technology, TeamDirectory, Measurement, \
    MeasurementNumber, LowMagReference, ZPlanes, MagBinOverlap, Tissue, Background, Genotype, Age
from experiments.xls import xls_logger as logger
from experiments.xls.date_parsers import DateParserFactory

MODELS_MAPPING: Dict[str, Callable[[str], models.Model]] = {
    ZPLANES: lambda name: ZPlanes.objects.get(name=name),
    TECHNOLOGY: lambda name: Technology.objects.get(name=name),
    LOW_MAG_REFERENCE: lambda name: LowMagReference.objects.get(name=name),
    TEAM_DIR: lambda name: TeamDirectory.objects.get(name=name),
    TISSUE: lambda name: Tissue.objects.get_or_create(name=name)[0],
    BACKGROUND: lambda name: Background.objects.get_or_create(name=name)[0],
    GENOTYPE: lambda name: Genotype.objects.get_or_create(name=name)[0],
    AGE: lambda name: Age.objects.get_or_create(name=name)[0]
}


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
        section_numbers = self._parse_section_numbers(self.row[SECTION_NUM])
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
    def _parse_date(datestring: Union[str, Timestamp]):
        return DateParserFactory.get_parser(datestring).parse()

    def _parse_optional_column(self, column: str) -> Union[models.Model, None]:
        name = self.row.get(column, '')
        if pd.isnull(name):
            return None
        try:
            return MODELS_MAPPING[column](name)
        except KeyError:
            raise NotImplementedError(f"Column {column} is not mapped to a processing function")

    def _parse_automated_sliden(self, automated_plateid: str) -> str:
        slide_n = self.row.get(AUTOMATED_SLIDEN, None)
        if automated_plateid and not slide_n:
            raise ValueError("Automated slide number is required if automated plate ID is provided")
        return slide_n

    def get_params(self) -> MeasurementParameters:
        # required fields
        try:
            uuid = self.row[UUID]
            researcher = Researcher.objects.get(employee_key=self.row[RESEARCHER])
            image_cycle = self.row[IMAGE_CYCLE]
            mag_bin_overlap = MagBinOverlap.objects.get(name=self.row[MAG_BIN_OVERLAP])
            automated_slide_id = self.row[SLIDE_ID]
            measurement = MeasurementNumber.objects.get(name=self.row[MEASUREMENT])
            sections = self._parse_sections()
            channel_targets = self._parse_channel_targets()
            date = self._parse_date(self.row[DATE])

            # optional fields
            technology = self._parse_optional_column(TECHNOLOGY)
            low_mag_ref = self._parse_optional_column(LOW_MAG_REFERENCE)
            z_planes = self._parse_optional_column(ZPLANES)
            automated_plate_id = self.row.get(AUTOMATED_PLATEID)
            automated_sliden = self._parse_automated_sliden(automated_plate_id)
            notes1 = self.row.get(NOTES_1)
            notes2 = self.row.get(NOTES_2)
            exp_location = self.row.get(EXPORT_LOCATION)
            arch_location = self.row.get(ARCHIVE_LOCATION)
            team_dir = self._parse_optional_column(TEAM_DIR)
        except KeyError as e:
            raise ValueError(f"A required column is absent: {e}")
        except (ValueError, ObjectDoesNotExist) as e:
            raise ValueError(f"{e}")

        model = Measurement(uuid=uuid,
                            researcher=researcher,
                            technology=technology,
                            automated_slide_id=automated_slide_id,
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
