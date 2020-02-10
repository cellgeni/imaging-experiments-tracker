from experiments.models import Analysis, Status


def submit_analysis(analysis: Analysis):
    analysis.status = Status.STARTED
    analysis.save()
