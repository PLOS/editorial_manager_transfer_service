__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from plugins.editorial_manager_transfer_service import forms
from plugins.editorial_manager_transfer_service.logic import get_plugin_settings, save_plugin_settings
from security import decorators


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
        journal_code,
    ) = get_plugin_settings(request.journal)

    if request.POST:
        form = forms.EditorialManagerTransferServiceForm(request.POST)

        if form.is_valid():
            submission_partner_code = form.cleaned_data["submission_partner_code"]
            license_code = form.cleaned_data["license_code"]
            journal_code = form.cleaned_data["journal_code"]

            save_plugin_settings(
                submission_partner_code,
                license_code,
                journal_code,
                request,
            )

    else:
        form = forms.EditorialManagerTransferServiceForm(
            initial={
                "submission_partner_code": submission_partner_code,
                "license_code": license_code,
                "journal_code": journal_code,
            }
        )

    template = 'editorial_manager_transfer_service/manager.html'
    context = {
        'form': form,
    }

    return render(request, template, context)
