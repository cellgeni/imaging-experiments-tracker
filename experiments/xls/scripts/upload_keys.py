"""
Command-line script to upload keys from an XLS file.
"""

import os
import sys

import django

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaging_tracking.settings")
    django.setup()

from experiments.xls.keys_importer import ColumnXLSImporter

filename = sys.argv[1]
ColumnXLSImporter(filename).import_all_columns()
