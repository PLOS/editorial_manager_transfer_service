__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

from typing import List

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from journal.models import Journal
from plugins.editorial_manager_transfer_service import forms
from plugins.editorial_manager_transfer_service.enums.report_state import ReportState
from plugins.editorial_manager_transfer_service.models import TransferReport, TransferLogs
from plugins.editorial_manager_transfer_service.utils.settings import get_plugin_settings, save_plugin_settings
from plugins.production_transporter.utilities import data_fetch
from security import decorators
from utils.logger import get_logger

logger = get_logger(__name__)


@staff_member_required
@decorators.has_journal
def manager(request):
    """
    The manager view for the Editorial Manager Service.
    :param request: the request object
    """
    (
        submission_partner_code,
        license_code,
        em_journal_code,
    ) = get_plugin_settings(request.journal, True)

    if request.POST:
        form = forms.EditorialManagerTransferServiceForm(request.POST)

        if form.is_valid():
            submission_partner_code = form.cleaned_data["submission_partner_code"]
            license_code = form.cleaned_data["license_code"]
            em_journal_code = form.cleaned_data["journal_code"]

            save_plugin_settings(
                    request.journal,
                    submission_partner_code,
                    license_code,
                    em_journal_code,
            )

            messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Form saved.',
            )
        else:
            messages.add_message(
                    request,
                    messages.ERROR,
                    'Error saving form.',
            )

    else:
        form = forms.EditorialManagerTransferServiceForm(
                initial={
                    "submission_partner_code": submission_partner_code,
                    "license_code": license_code,
                    "journal_code": em_journal_code,
                }
        )

    template = 'editorial_manager_transfer_service/manager.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@staff_member_required
@decorators.has_journal
def transfer_report(request):
    journal: Journal = request.journal

    if request.POST:
        if "send_article" in request.POST:
            article_id_str: str | None = request.POST.get('send_article')
            transfer_report_resend_article(request, journal, article_id_str)

    template = 'editorial_manager_transfer_service/listing.html'
    failed_bundle_transfer_reports = list(TransferReport.objects.filter(
            journal=journal, report_state=ReportState.FAILED_BUNDLING).select_related("article").only("id",
                                                                                                      "message_date_time_start",
                                                                                                      "article__id",
                                                                                                      "article__title").order_by(
            "-message_date_time_start"))

    context = {'journal': journal,
               'failed_bundle_transfer_reports': failed_bundle_transfer_reports}

    return render(request, template, context)


def transfer_report_resend_article(request, journal: Journal, article_id_str: str | None):
    if not article_id_str:
        logger.error(f"No article ID provided for {journal.code} when trying to send article to Editorial Manager.")
        return

    try:
        article_id = int(article_id_str)
    except ValueError:
        logger.error(f"Could not convert article ID {article_id_str} to an integer.")
        return

    from plugins.production_transporter.utils import schedule_file_transfer
    schedule_file_transfer(request, journal.code, article_id=article_id)


@staff_member_required
@decorators.has_journal
def transfer_article_reports(request, article_id: int | None = None):
    journal: Journal = request.journal

    article = data_fetch.fetch_article(journal, article_id)
    if not article:
        raise Exception("No article found")

    template = 'editorial_manager_transfer_service/article_report_listing.html'
    reports = list(TransferReport.objects.filter(journal=journal, article=article).defer("article", "journal").order_by(
            "-message_date_time_start"))

    context = {'journal': journal,
               'reports': reports,
               'article': article}

    return render(request, template, context)


@staff_member_required
@decorators.has_journal
def transfer_report_logs(request, report_id: str | None = None):
    journal: Journal = request.journal
    template = 'editorial_manager_transfer_service/report_listing.html'
    report = TransferReport.objects.filter(id=report_id).select_related("article").only("id", "article__id",
                                                                                        "article__title").first()
    logs: List[TransferLogs] = list(
            TransferLogs.objects.filter(report=report).defer("report", "article", "journal").order_by(
                    "-message_date_time"))

    context = {'journal': journal,
               'report': report,
               'logs': logs}

    return render(request, template, context)
