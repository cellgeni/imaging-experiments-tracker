import enum

ID = 'ID'
RESEARCHER = "Researcher"
PROJECT = "Project"
SLIDE_ID = "SlideID"
SLIDE_BARCODE = "Slide_barcode"
AUTOMATED_PLATEID = "Automated_PlateID"
AUTOMATED_SLIDEN = "SlideN"
SPECIES = "Species"
TISSUE = "Tissue"
TISSUE1 = TISSUE + "_1"
TISSUE2 = TISSUE + "_2"
TISSUE3 = TISSUE + "_3"
TISSUE4 = TISSUE + "_4"
SAMPLE = "Sample"
SAMPLE1 = SAMPLE + "_1"
SAMPLE2 = SAMPLE + "_2"
SAMPLE3 = SAMPLE + "_3"
SAMPLE4 = SAMPLE + "_4"
AGE = "Age"
AGE1 = AGE + "_1"
AGE2 = AGE + "_2"
AGE3 = AGE + "_3"
AGE4 = AGE + "_4"
BACKGROUND = "Background"
BACKGROUND1 = BACKGROUND + "_1"
BACKGROUND2 = BACKGROUND + "_2"
BACKGROUND3 = BACKGROUND + "_3"
BACKGROUND4 = BACKGROUND + "_4"
GENOTYPE = "Genotype"
GENOTYPE1 = GENOTYPE + "_1"
GENOTYPE2 = GENOTYPE + "_2"
GENOTYPE3 = GENOTYPE + "_3"
GENOTYPE4 = GENOTYPE + "_4"
TECHNOLOGY = "Technology"
IMAGE_CYCLE = "Image_cycle"
CHANNEL = "Channel"
CHANNEL1 = CHANNEL + "1"
CHANNEL2 = CHANNEL + "2"
CHANNEL3 = CHANNEL + "3"
CHANNEL4 = CHANNEL + "4"
CHANNEL5 = CHANNEL + "5"
CHANNEL6 = CHANNEL + "6"
CHANNEL7 = CHANNEL + "7"
TARGET = "Target"
TARGET1 = TARGET + "1"
TARGET2 = TARGET + "2"
TARGET3 = TARGET + "3"
TARGET4 = TARGET + "4"
TARGET5 = TARGET + "5"
TARGET6 = TARGET + "6"
TARGET7 = TARGET + "7"
CHANNEL_TARGET = "Channel-Target"
CHANNEL_TARGET1 = CHANNEL_TARGET + "1"
CHANNEL_TARGET2 = CHANNEL_TARGET + "2"
CHANNEL_TARGET3 = CHANNEL_TARGET + "3"
CHANNEL_TARGET4 = CHANNEL_TARGET + "4"
CHANNEL_TARGET5 = CHANNEL_TARGET + "5"
DATE = "Date"
MEASUREMENT_NUMBER = "Measurement"
LOW_MAG_REFERENCE = "Low_mag_reference"
MAG_BIN_OVERLAP = "Mag_Bin_Overlap"
SECTION_NUM = "SectionN"
SECTIONS = "Sections"
ZPLANES = "z-planes"
NOTES_1 = "Notes_1"
NOTES_2 = "Notes_2"
POST_STAIN = "Post-stain"
EXPORT_LOCATION = "Export_location"
ARCHIVE_LOCATION = "Archive_location"
TEAM_DIR = "Team_dir"
HARMONY_COPY = "Harmony_copy_deleted"
MAX_CHANNELS = 7  # maximum number of channels per measurement
MAX_SLOTS = 4  # maximum number of slots in a plate
DATE_FORMAT = "%d.%m.%Y"
METABASE_DATE_FORMAT = "%Y-%m-%dT00:00:00Z"

CHANNEL_TARGET_MAPPING = {
    CHANNEL1: TARGET1,
    CHANNEL2: TARGET2,
    CHANNEL3: TARGET3,
    CHANNEL4: TARGET4,
    CHANNEL5: TARGET5
}

METABASE_ID = "measurement_id"
METABASE_RESEARCHER = "researcher"
METABASE_PROJECT = "project"
METABASE_AUTOMATED_PLATEID = "automated_plate_id"
METABASE_SLIDE_ID = "automated_slide_id"
METABASE_AUTOMATED_SLIDEN = "automated_slide_num"
METABASE_IMAGE_CYCLE = "image_cycle"
METABASE_SLIDE_BARCODE = "slide_barcode"
METABASE_TECHNOLOGY = "technology"
METABASE_DATE = "date"
METABASE_MEASUREMENT_NUMBER = "measurement_number"
METABASE_LOW_MAG_REFERENCE = "low_mag_reference"
METABASE_MAG_BIN_OVERLAP = "mag_bin_overlap"
METABASE_ZPLANES = "zplanes"
METABASE_NOTES_1 = "notes_1"
METABASE_NOTES_2 = "notes_2"
METABASE_POST_STAIN = "post_stain"
METABASE_HARMONY_COPY = "harmony_copy_deleted"
METABASE_EXPORT_LOCATION = "export_location"
METABASE_ARCHIVE_LOCATION = "archive_location"
METABASE_TEAM_DIR = "team_directory"
METABASE_SAMPLES = "samples"
METABASE_CHANNEL_TARGETS = "channel_targets"
METABASE_SAMPLES_ATTRIBUTES_SEPARATOR = " | "
METABASE_CHANNEL_TARGETS_SEPARATOR = " -> "
METABASE_ENTITIES_SEPARATOR = ";; "

METABASE_TO_TEMPLATE_MAPPING = {
    METABASE_ID: ID,
    METABASE_RESEARCHER: RESEARCHER,
    METABASE_PROJECT: PROJECT,
    METABASE_AUTOMATED_PLATEID: AUTOMATED_PLATEID,
    METABASE_SLIDE_ID: SLIDE_ID,
    METABASE_AUTOMATED_SLIDEN: AUTOMATED_SLIDEN,
    METABASE_IMAGE_CYCLE: IMAGE_CYCLE,
    METABASE_SLIDE_BARCODE: SLIDE_BARCODE,
    METABASE_TECHNOLOGY: TECHNOLOGY,
    METABASE_DATE: DATE,
    METABASE_MEASUREMENT_NUMBER: MEASUREMENT_NUMBER,
    METABASE_LOW_MAG_REFERENCE: LOW_MAG_REFERENCE,
    METABASE_MAG_BIN_OVERLAP: MAG_BIN_OVERLAP,
    METABASE_ZPLANES: ZPLANES,
    METABASE_NOTES_1: NOTES_1,
    METABASE_NOTES_2: NOTES_2,
    METABASE_POST_STAIN: POST_STAIN,
    METABASE_HARMONY_COPY: HARMONY_COPY,
    METABASE_EXPORT_LOCATION: EXPORT_LOCATION,
    METABASE_ARCHIVE_LOCATION: ARCHIVE_LOCATION,
    METABASE_TEAM_DIR: TEAM_DIR
}
TEMPLATE_TO_METABASE_MAPPING = dict((y, x) for x, y in METABASE_TO_TEMPLATE_MAPPING.items())

SAMPLES = [SAMPLE1, SAMPLE2, SAMPLE3, SAMPLE4]
EXCEL_COLUMNS = [RESEARCHER, PROJECT, SLIDE_ID, AUTOMATED_PLATEID, AUTOMATED_SLIDEN, SLIDE_BARCODE,
                 TECHNOLOGY, IMAGE_CYCLE, SPECIES,
                 SAMPLE1, TISSUE1, AGE1, BACKGROUND1, GENOTYPE1,
                 SAMPLE2, TISSUE2, AGE2, BACKGROUND2, GENOTYPE2,
                 SAMPLE3, TISSUE3, AGE3, BACKGROUND3, GENOTYPE3,
                 SAMPLE4, TISSUE4, AGE4, BACKGROUND4, GENOTYPE4,
                 CHANNEL1, TARGET1,
                 CHANNEL2, TARGET2,
                 CHANNEL3, TARGET3,
                 CHANNEL4, TARGET4,
                 CHANNEL5, TARGET5,
                 CHANNEL6, TARGET6,
                 CHANNEL7, TARGET7,
                 DATE, MAG_BIN_OVERLAP, LOW_MAG_REFERENCE, SECTION_NUM, NOTES_1, NOTES_2, POST_STAIN,
                 ZPLANES,
                 EXPORT_LOCATION, ARCHIVE_LOCATION, TEAM_DIR, HARMONY_COPY
                 ]

REQUIRED_COLUMNS = {RESEARCHER, PROJECT, SLIDE_ID, SLIDE_BARCODE, TISSUE1, SAMPLE1, CHANNEL1, TARGET1,
                    IMAGE_CYCLE, DATE, MEASUREMENT_NUMBER, MAG_BIN_OVERLAP, LOW_MAG_REFERENCE, SECTION_NUM}

DELETE_PERMISSION = "delete"
VIEW_PERMISSION = "view"
CREATE_OR_UPDATE_PERMISSION = "create"


class Role(enum.Enum):
    OWNER = "owner"
    SIMPLE_USER = "simple user"
    VIEWER = "viewer"
