__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

from typing import List

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.shortcuts import render
from journal.models import Journal
from plugins.editorial_manager_transfer_service import forms
from plugins.editorial_manager_transfer_service.enums.report_state import ReportState
from plugins.editorial_manager_transfer_service.forms import EditorialManagerTransferServiceSectionEditorForm
from plugins.editorial_manager_transfer_service.models import TransferReport, TransferLogs, EditorialManagerSection
from plugins.editorial_manager_transfer_service.utils.settings import get_plugin_settings, save_plugin_settings
from plugins.production_transporter.utilities import data_fetch
from security import decorators
from submission.models import Section
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
def manager_sections(request):
    journal: Journal = request.journal

    template = 'editorial_manager_transfer_service/editorial_manager_sections.html'
    janeway_sections = list(Section.objects.filter(journal=journal).order_by("-name"))
    sections = []
    for janeway_section in janeway_sections:
        em_section = EditorialManagerSection.objects.filter(section=janeway_section).first()

        section = {
            "janeway_section": janeway_section,
            "em_section": em_section,
        }
        sections.append(section)

    context = {'journal': journal,
               'sections': sections}

    return render(request, template, context)

def manager_section_editor(request, section_id: int | None = None):
    """
    Manage an individual section.
    :param request:
    :param section_id:
    :return:
    """
    journal: Journal = request.journal

    template = 'editorial_manager_transfer_service/editorial_manager_section_editor.html'
    janeway_section: Section = Section.objects.filter(id=section_id).first()

    if janeway_section is None:
        raise Exception("No section found")

    em_section = EditorialManagerSection.objects.filter(section=janeway_section).first()
    em_section_id = None
    if em_section is not None:
        em_section_id = em_section.editorial_manager_section_id

    if request.POST:
        logger.debug("Beginning to save Editorial Manager Section...")
        form = forms.EditorialManagerTransferServiceSectionEditorForm(request.POST)

        if form.is_valid():
            new_em_section_id = form.cleaned_data["em_section_id"]
            janeway_section_name = form.cleaned_data["janeway_section_name"]

            # Update the section name if it changed.
            if janeway_section_name != janeway_section.name:
                janeway_section.name = janeway_section_name
                janeway_section.save()

            # Update the em_section_id
            update_em_section_id(janeway_section, em_section_id, new_em_section_id)

            # Update references.
            em_section = EditorialManagerSection.objects.filter(section=janeway_section).first()
            em_section_id = None
            if em_section is not None:
                em_section_id = em_section.editorial_manager_section_id

    form = EditorialManagerTransferServiceSectionEditorForm(
                initial={
                    "em_section_id": em_section_id,
                    "janeway_section_name": janeway_section.name,
                }
            )

    section = {
        "janeway_section": janeway_section,
        "em_section": em_section,
    }

    context = {'journal': journal,
               'section': section,
               "form": form,}

    return render(request, template, context)

def update_em_section_id(section: Section, old_id: str | None = None, new_id: str | None = None) -> None:
    """
    Updates the EM section ID, if required.
    :param section: The section to update.
    :param old_id: The old EM section ID.
    :param new_id: The new EM section ID.
    """
    if not old_id:
        old_id = ""

    if not new_id:
        new_id = ""

    new_id = new_id.strip().lower()
    old_id = old_id.strip().lower()

    # Nothing to do.
    if old_id == new_id:
        logger.info(f"EM section ID is same.")
        return

    # Means the old ID existed, but the new ID does not.
    if new_id == "":
        EditorialManagerSection.objects.filter(section=section).delete()
        logger.info(f"EM section ID deleted.")
        return

    em_section = EditorialManagerSection.objects.get_or_create(section=section)[0]
    em_section.editorial_manager_section_id = new_id
    em_section.save()
    logger.info(f"EM section id {old_id} updated to {new_id}")


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
