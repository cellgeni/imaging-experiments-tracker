import datetime
from experiments.constants import CREATE_OR_UPDATE_PERMISSION, DELETE_PERMISSION, ExportStatus
from experiments.image_file_checker import ImagePathChecker
from experiments.models.measurement import Project
from typing import Union

from experiments import RowT
from experiments import auth
from experiments.models import Measurement, Slot, AutomatedSlide, Plate, MeasurementNumber
from experiments.xls import EntitiesImporter, xls_logger as logger
from experiments.xls.row_parser import XLSRowParser, ChannelTargetParser


def check_image_file_paths(measurement: Measurement):
    if measurement.exported and measurement.export_status in (ExportStatus.NOT_VERIFIED, ExportStatus.FILES_NOT_PRESENT):
        ipc = ImagePathChecker(measurement)
        ipc.check_paths()


class MeasurementModifier(EntitiesImporter):

    def __init__(self, row: RowT):
        super(MeasurementModifier, self).__init__(row)
        self.parser = XLSRowParser(row)

    def get_or_create_slot(self, measurement: Measurement) -> Slot:
        automated_slide = self.parser.parse_automated_slide()
        slot_num = self.parser.parse_automated_slide_num()
        return Slot.objects.get_or_create(automated_slide=automated_slide,
                                          automated_slide_num=slot_num,
                                          measurement=measurement)[0]

    def create_slot(self, measurement) -> None:
        """Create new slot and add it to the measurement."""
        slot = self.get_or_create_slot(measurement)
        self.add_sections(slot)

    def add_sections(self, slot) -> None:
        numbers = self.parser.parse_section_numbers()
        for section in self.parser.parse_sections():
            if section.number in numbers:
                slot.sections.add(section)

    def create_channel_targets(self, measurement: Measurement) -> None:
        for chtp in self.parser.parse_channel_targets():
            measurement.channel_target_pairs.add(chtp)


class MeasurementCreator(MeasurementModifier):

    def create_measurement(self) -> Measurement:
        """Create Measurement, channel-targets, slots."""
        measurement = self.parser.get_measurement()
        measurement.save()
        self.create_slot(measurement)
        self.create_channel_targets(measurement)
        return measurement


class MeasurementUpdater(MeasurementModifier):

    def __init__(self, row: RowT, original_measurement: Measurement):
        super().__init__(row)
        self.original_measurement = original_measurement

    def update(self) -> None:
        """Walk through the fields of all of the related entities and modify them if needed."""
        self.update_measurement_attributes()
        self.update_slot()

    def update_measurement_attributes(self) -> None:
        """Update Measurement object."""
        updated_measurement = self.parser.get_measurement()
        self.original_measurement.copy_non_core_attributes(updated_measurement)
        self.update_channel_targets()

    def update_channel_targets(self) -> None:
        """Remove the old channel targets if all new channel names are valid
        and add the new ones."""
        ChannelTargetParser(self.row).check_channels()
        self.original_measurement.channel_target_pairs.clear()
        self.create_channel_targets(self.original_measurement)

    def update_slot(self):
        slot = self.get_or_create_slot(self.original_measurement)
        slot.sections.clear()
        self.add_sections(slot)


class ExistingMeasurementFinder(EntitiesImporter):

    def __init__(self, row: RowT):
        super(ExistingMeasurementFinder, self).__init__(row)
        self.parser = XLSRowParser(row)

    def get_existing_measurement_from_a_row(self) -> Union[Measurement, None]:
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
                                   automated_slide: AutomatedSlide, slide_num: int) -> Union[Measurement, None]:
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


class MeasurementImporter(MeasurementModifier):

    def __init__(self, row: RowT, user_id: int):
        super().__init__(row)
        self.user_id = user_id

    def _check_permission_on_project(self, permission: str) -> None:
        """Check whether a user is authorized to do an action on measurements within a project from this row."""
        project = self.get_project()
        if not auth.check_permission(self.user_id, project.id, permission):
            raise PermissionError(f"User does not have {permission} permission on the project {project.name}")

    def import_measurement(self) -> Measurement:
        """Create or update a measurement from a row."""
        existing_measurement = self.find_existing_measurement()
        if existing_measurement:
            measurement = self.extend_or_update(existing_measurement)
        else:
            measurement = self.create_measurement()
        try:
            check_image_file_paths(measurement)
        except Exception: # todo: handle more gracefully
            pass
        return measurement

    def create_measurement(self) -> Measurement:
        """Create measurement from a row."""
        self._check_permission_on_project(CREATE_OR_UPDATE_PERMISSION)
        measurement = MeasurementCreator(self.row).create_measurement()
        logger.info(f"Imported measurement with id {measurement.id}")
        return measurement

    def extend_or_update(self, existing_measurement: Measurement) -> Measurement:
        """Add a new slot to a measurement or update the existing slot."""
        self._check_permission_on_project(CREATE_OR_UPDATE_PERMISSION)
        if existing_measurement.has_slide_number(self.parser.parse_automated_slide_num()):
            MeasurementUpdater(self.row, existing_measurement).update()
            logger.info(
                f"Updated measurement with id {existing_measurement.id}")
        else:
            self.create_slot(existing_measurement)
            logger.info(
                f"Created new slot in measurement with id {existing_measurement.id}")
        return existing_measurement

    def delete_measurement(self) -> bool:
        """Delete a measurement and return True if was deleted or False if not found"""
        existing_measurement = self.find_existing_measurement()
        return existing_measurement is not None and self._check_permission_and_delete_measurement(existing_measurement)

    def _check_permission_and_delete_measurement(self, measurement: Measurement) -> bool:
        """If a user has permission to delete a measurement, delete it, raise an error otherwise."""
        if measurement.project == self.get_project():
            self._check_permission_on_project(DELETE_PERMISSION)
            measurement.delete()
            return True
        else:
            raise ValueError(
                "Project in the row doesn't match the project in the existing measurement")

    def find_existing_measurement(self) -> Union[Measurement, None]:
        return ExistingMeasurementFinder(self.row).get_existing_measurement_from_a_row()

    def get_project(self) -> Project:
        return self.parser.parse_project()
