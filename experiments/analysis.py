from experiments.models import Analysis, Status


def submit_analysis(analysis: Analysis):
    """
    Handles analysis request submission
    """
    analysis.status = Status.STARTED
    analysis.save()
