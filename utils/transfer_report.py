from django.utils.timezone import now
from journal.models import Journal
from plugins.editorial_manager_transfer_service.enums.report_state import ReportState
from plugins.editorial_manager_transfer_service.models import TransferReport
from submission.models import Article


def get_or_create_transfer_report(journal: Journal, article: Article) -> TransferReport:
    """
    Gets or creates a new TransferReport based on the given information.
    :param journal: The journal to use.
    :param article: The article to use.
    :return: A new or existing TransferReport.
    """
    try:
        transfer_reports = TransferReport.objects.filter(journal=journal, article=article,
                                                         resolved=False).order_by("-message_date_time_start")
        if len(transfer_reports) > 0:
            return transfer_reports[0]

        transfer_report = TransferReport.objects.create(journal=journal, article=article, )
    except TransferReport.DoesNotExist:
        raise TransferReport.DoesNotExist()
    return transfer_report


def resolve_transfer_report(transfer_report: TransferReport) -> None:
    transfer_report.resolved = True
    transfer_report.report_state = ReportState.NORMAL
    transfer_report.message_date_time_stop = now()
    transfer_report.save()
