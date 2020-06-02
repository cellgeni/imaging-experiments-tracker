import logging
import os
from typing import Callable, Dict, Union

import pandas as pd
from django.db import models

from experiments import RowT
from experiments.constants import *
from experiments.models import (Age, ArchiveLocation, AutomatedSlide,
                                Background, ExportLocation, Genotype,
                                LowMagReference, MagBinOverlap,
                                MeasurementNumber, Plate, Project, Researcher,
                                TeamDirectory, Technology, Tissue, ZPlanes)

EXCEL_TEMPLATE = os.path.join(os.path.dirname(__file__), "measurements_input.xlsx")

logging.basicConfig(level=logging.INFO)
xls_logger = logging.getLogger(__name__)

# a corresponding object given an input string
MODELS_MAPPING: Dict[str, Callable[[str], models.Model]] = {
    ZPLANES: lambda name: ZPlanes.objects.get_or_create(name=name)[0],
    TECHNOLOGY: lambda name: Technology.objects.get(name=name),
    AUTOMATED_PLATEID: lambda name: Plate.objects.get_or_create(name=name)[0],
    SLIDE_ID: lambda name: AutomatedSlide.objects.get_or_create(name=name)[0],
    EXPORT_LOCATION: lambda name: ExportLocation.objects.get_or_create(name=name)[0],
    ARCHIVE_LOCATION: lambda name: ArchiveLocation.objects.get_or_create(name=name)[0],
    LOW_MAG_REFERENCE: lambda name: LowMagReference.objects.get_or_create(name=name)[0],
    MAG_BIN_OVERLAP: lambda name: MagBinOverlap.objects.get_or_create(name=name)[0],
    TEAM_DIR: lambda name: TeamDirectory.objects.get_or_create(name=name)[0],
    TISSUE: lambda name: Tissue.objects.get_or_create(name=name)[0],
    BACKGROUND: lambda name: Background.objects.get_or_create(name=name)[0],
    GENOTYPE: lambda name: Genotype.objects.get_or_create(name=name)[0],
    AGE: lambda name: Age.objects.get_or_create(name=name)[0],
    RESEARCHER: lambda name: Researcher.objects.get(login=name),
    PROJECT: lambda name: Project.objects.get(name=name),
    MEASUREMENT_NUMBER: lambda name: MeasurementNumber.objects.get_or_create(name=name)[0]
}


class EntitiesImporter:
    """Base class for importing entities from a row. Contains a row"""

    def __init__(self, row: Union[pd.Series, RowT]):
        self.row = row
