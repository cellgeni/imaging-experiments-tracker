from typing import List, Dict

from experiments.models import *
from experiments.constants import *

MAX_ROWS = 100


class ImageTrackerColumn:

    def __init__(self, column_header: str, validation_rules: Dict = None, column_width: int = 20):
        self.column_header = column_header
        self.column_width = column_width
        self.validation_rules = validation_rules or dict()

    def prepopulate(self, column, worksheet):
        pass

    def write(self, column, worksheet):
        worksheet.write(0, column, self.column_header)
        worksheet.set_column(column, column, self.column_width)
        worksheet.data_validation(1, column, MAX_ROWS, column, self.validation_rules)
        self.prepopulate(column, worksheet)


class UUIDColumn(ImageTrackerColumn):

    def __init__(self):
        super().__init__(UUID, {})

    def prepopulate(self, column, worksheet):
        for row in range(1, 21):
            worksheet.write(row, column, str(uuid.uuid4()))


class ModeColumn(ImageTrackerColumn):

    def __init__(self):
        super().__init__(MODE, {'validate': 'list',
                                'value': [mode.value for mode in MeasurementModes],
                                'input_title': "Mode",
                                'input_message': "Choose mode"})

    def prepopulate(self, column, worksheet):
        for row in range(1, 21):
            worksheet.write(row, column, MeasurementModes.IGNORE)


def get_columns() -> List[ImageTrackerColumn]:
    uuid_column = UUIDColumn()
    mode_column = ModeColumn()
    researcher = ImageTrackerColumn(RESEARCHER, {'validate': 'list',
                                                 'value': [r.employee_key for r in Researcher.objects.all()],
                                                 'input_title': "Researcher",
                                                 'input_message': "Choose researcher"})
    project = ImageTrackerColumn(PROJECT, {'validate': 'list',
                                           'value': [r.key for r in CellGenProject.objects.all()],
                                           'input_title': "Project",
                                           'input_message': "Choose project"})
    slide_id = ImageTrackerColumn(SLIDE_ID, {})
    automated_plate_id = ImageTrackerColumn(AUTOMATED_PLATEID, {})
    automated_sliden = ImageTrackerColumn(AUTOMATED_SLIDEN, {'validate': 'integer',
                                                             'criteria': '>',
                                                             'value': 0})
    slide_barcode = ImageTrackerColumn(SLIDE_BARCODE, {
        'validate': 'list',
        'value': [sl.barcode_id for sl in Slide.objects.all()],
        'input_title': "Slide",
        'input_message': "Choose slide"
    })
    technology = ImageTrackerColumn(TECHNOLOGY, {'validate': 'list',
                                                 'value': [t.name for t in Technology.objects.all()],
                                                 'input_title': "Technology",
                                                 'input_message': "Choose technology"})
    image_cycle = ImageTrackerColumn(IMAGE_CYCLE, {'validate': 'integer',
                                                   'criteria': '<',
                                                   'value': 10})
    channel_target_validation = {
        'validate': 'list',
        'value': [str(ct) for ct in ChannelTarget.objects.all()],
        'input_title': "Channel-target pair",
        'input_message': "Choose channel-target pair"
    }
    channel_target1 = ImageTrackerColumn(CHANNEL_TARGET1, channel_target_validation)
    channel_target2 = ImageTrackerColumn(CHANNEL_TARGET2, channel_target_validation)
    channel_target3 = ImageTrackerColumn(CHANNEL_TARGET3, channel_target_validation)
    channel_target4 = ImageTrackerColumn(CHANNEL_TARGET4, channel_target_validation)
    channel_target5 = ImageTrackerColumn(CHANNEL_TARGET5, channel_target_validation)
    date = ImageTrackerColumn(DATE, {'validate': 'date'})
    measurement = ImageTrackerColumn(MEASUREMENT, {})
    low_mag_reference = ImageTrackerColumn(LOW_MAG_REFERENCE, {})
    mag_bin_overlap = ImageTrackerColumn(MAG_BIN_OVERLAP, {})
    sectionN = ImageTrackerColumn(SECTION_NUM, {})
    z_planes = ImageTrackerColumn(ZPLANES, {})
    notes1 = ImageTrackerColumn(NOTES_1, {})
    notes2 = ImageTrackerColumn(NOTES_2, {})
    export_location = ImageTrackerColumn(EXPORT_LOCATION, {})
    archive_location = ImageTrackerColumn(ARCHIVE_LOCATION, {})
    team_dir = ImageTrackerColumn(TEAM_DIR, {'validate': 'list',
                                             'value': [t.name for t in TeamDirectory.objects.all()],
                                             'input_title': "Team directory",
                                             'input_message': "Choose team directory"})
    return [uuid_column, mode_column, researcher, project,
            slide_id, automated_plate_id, automated_sliden, slide_barcode,
            technology, image_cycle, channel_target1, channel_target2, channel_target3,
            channel_target4, channel_target5, date, measurement, low_mag_reference,
            mag_bin_overlap, sectionN, z_planes, notes1, notes2, export_location, archive_location,
            team_dir]
