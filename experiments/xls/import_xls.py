import logging
import traceback
from typing import Dict, List

import pandas as pd
from django.core.exceptions import ObjectDoesNotExist

from experiments.models import *
from experiments.constants import *

from xls.me import MeasurementParameters, MeasurementM2MFields

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MeasurementParametersParser:

    def __init__(self, row):
        self.row = row

    def _parse_sections(self) -> List[Section]:
        sections = []
        slide = Slide.objects.get(self.row[SLIDE_BARCODE])
        section_numbers = self.row[SECTIONS].split(",")
        for s in section_numbers:
            section = Section.objects.get(number=int(s),
                                          slide=slide)
            sections.append(section)
        return sections

    def _parse_channel_targets(self) -> List[ChannelTarget]:
        result = []
        for i in range(1, 6):
            if self.row[CHANNEL_TARGET]:
                channel, _, target = self.row[CHANNEL_TARGET + str(i)].split(" ")
                result.append(ChannelTarget.objects.get(channel=channel, target=target))
        return result

    def get_params(self) -> MeasurementParameters:

        uuid = self.row[UUID]
        researcher = Researcher.objects.get(employee_key=self.row[RESEARCHER])
        sections = self._parse_sections()
        technology = Technology.objects.get(name=self.row[TECHNOLOGY])
        image_cycle = self.row[IMAGE_CYCLE]
        channel_targets = self._parse_channel_targets()
        date = self.row[DATE]
        measuremet = self.row[MEASUREMENT]
        low_mag_ref = self.row[LOW_MAG_REFERENCE]
        automated_plate_id = self.row[AUTOMATED_PLATEID]
        automated_sliden = self.row[AUTOMATED_SLIDEN]
        mag_bin_overlap = self.row[MAG_BIN_OVERLAP]
        notes1 = self.row[NOTES_1]
        notes2 = self.row[NOTES_2]
        exp_location = self.row[EXPORT_LOCATION]
        arch_location = self.row[ARCHIVE_LOCATION]
        team_dir = self.row[TEAM_DIR]
        model = Measurement(id=uuid,
                            researcher=researcher,
                            technology=technology,
                            automated_plate_id=automated_plate_id,
                            automated_sliden=automated_sliden,
                            mag_bin_overlap=mag_bin_overlap,
                            notes1=notes1,
                            notes2=notes2,
                            export_location=exp_location,
                            archive_location=arch_location,
                            team_dir=team_dir,
                            low_mag_reference=low_mag_ref,
                            measurement=measuremet,
                            date=date,
                            image_cycle=image_cycle)
        m2mfields = MeasurementM2MFields(channel_targets, sections)
        return MeasurementParameters(model, m2mfields)


class ImageTrackingRow:

    def __init__(self, row):
        self.row = row

    def ignore(self):
        logger.info(f"Row ignored: {self.row}")

    def delete(self):
        uuid = self.row[UUID]
        try:
            Measurement.objects.get(uuid=uuid).delete()
            logger.info(f"Measurement with uuid {uuid} deleted")
        except ObjectDoesNotExist:
            logger.warning(f"Measurement with uuid {uuid} does not exist")

    @staticmethod
    def create(parameters: MeasurementParameters):
        parameters.create_db_object()
        logger.info(f"Created measurement with uuid {uuid}")

    def update(self, measurement: Measurement, parameters: MeasurementParameters):
        uuid = self.row[UUID]
        logger.info(f"Updated measurement with uuid {uuid}")

    def parse_parameters(self) -> MeasurementParameters:
        parser = MeasurementParametersParser(self.row)
        return parser.get_params()

    def create_or_update(self):
        parameters = self.parse_parameters()
        try:
            measurement = Measurement.objects.get(uuid=self.row[UUID])
            self.update(measurement, parameters)
        except ObjectDoesNotExist:
            self.create(parameters)

    def handle_mode(self):
        logger.info(f"Importing row {self.row}")
        mode = self.row[MODE]
        if mode == IGNORE:
            self.ignore()
        elif mode == CREATE_OR_UPDATE:
            self.create_or_update()
        elif mode == DELETE:
            self.delete()


class SpreadsheetImporter:

    def __init__(self, file):
        self.df = pd.read_excel(file)

    def import_spreadsheet(self):
        for index, row in self.df[1:].iterrows():
            rm = ImageTrackingRow(row)
            try:
                rm.handle_mode()
            except Exception:
                logger.error(f"Failed to import row with uuid {uuid}")
                traceback.print_exc()


if __name__ == "__main__":
    file = r'../measurements_input.xlsx'
    si = SpreadsheetImporter(file)
    si.import_spreadsheet()
