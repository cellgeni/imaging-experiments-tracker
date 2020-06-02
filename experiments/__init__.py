import os
from typing import Dict

from django.conf import settings

from experiments.authorization import Authorization

RowT = Dict[str, str]

auth = Authorization(os.path.join(settings.CASBIN_ROOT, "roles.yaml"))
