"""
Command-line script to upload measurements from spreadsheets in a directory.
"""
import logging
import os
import sys

import django

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaging_tracking.settings")
    django.setup()

from experiments.xls.view_importers import MeasurementsViewImporter


dir = sys.argv[1]
result_file = os.path.join(dir, "import_log.txt")
with open(result_file, 'w') as f:
    for filename in os.listdir(dir):
        try:
            logging.info(f"Importing file {filename}")
            log = MeasurementsViewImporter(os.path.join(dir, filename)).import_and_get_log()
            f.write(filename + '\n')
            for line in log:
                f.write(line + '\n')
            f.write("----------------------------------\n\n")
        except Exception:
            logging.info(f"Could not import file {filename}, skipped")
