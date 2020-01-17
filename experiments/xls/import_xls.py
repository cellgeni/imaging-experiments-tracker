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

    def __init__(self, row: pd.Series):
        self.row = row

    def _parse_sections(self) -> List[Section]:
        sections = []
        slide = Slide.objects.get(barcode_id=self.row[SLIDE_BARCODE])
        section_numbers = self.row[SECTIONS].split(",")
        for s in section_numbers:
            section = Section.objects.get(number=int(s),
                                          slide=slide)
            sections.append(section)
        return sections

    def _parse_channel_targets(self) -> List[ChannelTarget]:
        result = []
        for i in range(1, 6):
            column = CHANNEL_TARGET + str(i)
            if not pd.isnull(self.row.get(column)):
                channel, target = ChannelTarget.get_channel_and_target_from_str(self.row[column])
                result.append(ChannelTarget.objects.get(channel__name=channel, target__name=target))
        return result

    def get_params(self) -> MeasurementParameters:
        try:
            uuid = self.row[UUID]
            researcher = Researcher.objects.get(employee_key=self.row[RESEARCHER])
            sections = self._parse_sections()
            technology = Technology.objects.get(name=self.row[TECHNOLOGY])
            image_cycle = self.row[IMAGE_CYCLE]
            channel_targets = self._parse_channel_targets()
            date = self.row[DATE]
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
        model = Measurement(id=uuid,
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


class ImageTrackingRow:

    def __init__(self, row: pd.Series):
        self.row = row

    def ignore(self) -> None:
        logger.info(f"Row ignored: {self.row}")

    def delete(self) -> None:
        uuid = self.row[UUID]
        try:
            Measurement.objects.get(uuid=uuid).delete()
            logger.info(f"Measurement with uuid {uuid} deleted")
        except ObjectDoesNotExist:
            logger.warning(f"Measurement with uuid {uuid} does not exist")

    @staticmethod
    def create(parameters: MeasurementParameters) -> None:
        parameters.create_db_object()
        logger.info(f"Created measurement with uuid {uuid}")

    def update(self, measurement: Measurement, parameters: MeasurementParameters) -> None:
        uuid = self.row[UUID]
        logger.info(f"Updated measurement with uuid {uuid}")

    def parse_parameters(self) -> MeasurementParameters:
        parser = MeasurementParametersParser(self.row)
        return parser.get_params()

    def create_or_update(self) -> None:
        parameters = self.parse_parameters()
        try:
            measurement = Measurement.objects.get(id=self.row[UUID])
            self.update(measurement, parameters)
        except ObjectDoesNotExist:
            self.create(parameters)

    def handle_mode(self) -> None:
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

    def import_spreadsheet(self) -> None:
        for index, row in self.df.iterrows():
            rm = ImageTrackingRow(row)
            try:
                rm.handle_mode()
            except Exception as e:
                logger.error(f"Failed to import row with uuid {uuid}")
                traceback.print_exc()


if __name__ == "__main__":
    file = r'../measurements_input.xlsx'
    si = SpreadsheetImporter(file)
    si.import_spreadsheet()
