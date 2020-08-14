import logging
import os
from typing import Tuple
from urllib.parse import urljoin

import requests

from experiments.constants import ExportStatus
from experiments.models import Measurement, Slot

FS_SERVER = os.getenv("FS_SERVER")

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class ImagePathChecker:
    pattern = r'^%s[\w\-]+Measurement[\s]%s$'

    def __init__(self, measurement: Measurement):
        self.m = measurement

    def get_mes_identifier(self) -> str:
        if self.m.plate:
            return self.m.plate.name
        else:
            return Slot.get_automated_slide(self.m).name

    def create_path_regex(self) -> Tuple[str, str]:
        # construct root directory
        if not (self.m.team_directory and self.m.export_location):
            return "", ""
        rootdir = os.path.join(self.m.team_directory.name, self.m.export_location.name.replace("\\", "/"))
        id_ = self.get_mes_identifier()
        return rootdir, self.pattern % (id_, self.m.measurement_number.name)

    def check_paths(self) -> None:
        rootdir, path_regex = self.create_path_regex()
        logger.info(f"Rootdir: {rootdir}")
        logger.info(f"Path regex: {path_regex}")
        if rootdir and path_regex:
            self.run_path_checking(rootdir, path_regex)
        else:
            logging.info(f"Some metadata missing, rootdir: {rootdir}, path regex: {path_regex}")
            self.m.export_status = ExportStatus.METADATA_MISSING
            self.m.save()

    def run_path_checking(self, rootdir: str, path_regex: str) -> None:
        params = {
            "rootdir": rootdir,
            "regex_pattern": path_regex
        }
        res = requests.get(FS_SERVER, params)
        path = res.text
        if path.startswith("/"):
            self.update_file_path(path)
            logger.info(f"Files present for path {path}")
        else:
            self.set_export_status(ExportStatus.FILES_NOT_PRESENT)
            logger.info(f"Files not present for directory {rootdir} and pattern {path_regex}")

    def update_file_path(self, file_path: str) -> None:
        self.m.files_path = file_path
        self.m.exported = True
        self.m.save()
        self.set_export_status(ExportStatus.FILES_PRESENT)

    def set_export_status(self, status: ExportStatus) -> None:
        self.m.export_status = status
        self.m.save()


class Stitcher:

    STITCHING_DIR = "/nfs/team283_imaging/0HarmonyStitched"
    STITCHING_URL = urljoin(FS_SERVER, "stitching")

    def stitch(self, measurement: Measurement):
        measurement_relative_dir = measurement.files_path.split("/")[-1]
        params = {
            "input_dir": os.path.join(measurement.files_path, "Images", "Index.idx.xml"),
            "output_dir": os.path.join(self.STITCHING_DIR, measurement.project.name, measurement_relative_dir)
        }
        requests.post(self.STITCHING_URL, json=params)
