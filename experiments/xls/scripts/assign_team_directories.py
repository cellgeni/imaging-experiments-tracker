
import os

import django


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "imaging_tracking.settings")
    django.setup()

from experiments.models import Measurement, TeamDirectory
from experiments.image_files_operations import ImagePathChecker

# td = TeamDirectory.objects.get_or_create(name="team283_imaging")[0]
# for m in Measurement.objects.all():
#     m.team_directory = td
#     m.save()
for m in Measurement.objects.all():
    ipc = ImagePathChecker(m)
    ipc.check_paths()