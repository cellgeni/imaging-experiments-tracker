import datetime
from typing import Union

from experiments.models import Measurement, Slot, AutomatedSlide, Plate, MeasurementNumber
from experiments.constants import *
from experiments.xls import EntitiesImporter, xls_logger as logger
from experiments.xls.row_parser import XLSRowParser


class MeasurementModifier(EntitiesImporter):

    def __init__(self, row):
        super(MeasurementModifier, self).__init__(row)
        self.parser = XLSRowParser(row)

    def create_slot(self, measurement) -> None:
        """Create new slot and add it to the measurement."""
        automated_slide = self.parser.parse_automated_slide()
        slot_num = self.parser.parse_automated_slide_num()
        slot = Slot.objects.create(automated_slide=automated_slide,
                                   automated_slide_num=slot_num,
                                   measurement=measurement)
        self.add_sections(slot)

    def add_sections(self, slot) -> None:
        numbers = self.parser.parse_section_numbers()
        for section in self.parser.parse_sections():
            if section.number in numbers:
                slot.sections.add(section)


class MeasurementCreator(MeasurementModifier):

    def create_measurement(self) -> Measurement:
        """Create Measurement, channel-targets, slots."""
        measurement = self.parser.get_measurement()
        measurement.save()
        self.create_slot(measurement)
        self.create_channel_targets(measurement)
        return measurement

    def create_channel_targets(self, measurement: Measurement) -> None:
        for chtp in self.parser.parse_channel_targets():
            measurement.channel_target_pairs.add(chtp)


class MeasurementUpdater(MeasurementModifier):

    def update(self, measurement: Measurement) -> None:
        """Walk through the fields of all of the related entities and modify them if needed."""
        pass


class MeasurementImporter(MeasurementModifier):

    def import_measurement(self) -> Measurement:
        existing_measurement = self.find_existing_measurement()
        if existing_measurement:
            return self.extend_or_update(existing_measurement)
        else:
            measurement = MeasurementCreator(self.row).create_measurement()
            logger.info(f"Imported measurement with id {measurement.id}")
            return measurement

    def extend_or_update(self, existing_measurement: Measurement) -> Measurement:
        if existing_measurement.has_slide_number(self.parser.parse_automated_slide_num()):
            MeasurementUpdater(self.row).update(existing_measurement)
            logger.info(f"Updated measurement with id {existing_measurement.id}")
        else:
            self.create_slot(existing_measurement)
            logger.info(f"Created new slot in measurement with id {existing_measurement.id}")
        return existing_measurement

    def find_existing_measurement(self) -> Union[Measurement, None]:
        """Find existing measurement from a row."""
        automated_slide = self.parser.parse_automated_slide()
        measurement_number = self.parser.parse_measurement_number()
        slide_num = self.parser.parse_automated_slide_num()
        plate = self.parser.parse_plate()
        date = self.parser.parse_date()
        return self._find_existing_measurement(plate, measurement_number, date,
                                               automated_slide, slide_num)

    @staticmethod
    def _find_existing_measurement(plate: Plate,
                                   measurement_number: MeasurementNumber, date: datetime.date,
                                   automated_slide: AutomatedSlide, slide_num: int) -> Measurement:
        if plate:
            return Measurement.objects.filter(plate=plate,
                                              measurement_number=measurement_number,
                                              date=date).first()
        else:
            slots = Slot.objects.filter(automated_slide=automated_slide,
                                        automated_slide_num=slide_num,
                                        measurement__measurement_number=measurement_number,
                                        measurement__date=date)
            if slots:
                return slots[0].measurement
