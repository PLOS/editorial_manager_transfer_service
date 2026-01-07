__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

from django import forms
from django.core.exceptions import ValidationError
import re


class EditorialManagerTransferServiceForm(forms.Form):
    """
    The form for the Editorial Manager Transfer Service
    """
    submission_partner_code = forms.CharField(required=False, help_text="Your organization's Submission Partner Code.")
    license_code = forms.CharField(required=False, help_text="The license code for your organization.")
    journal_code = forms.CharField(required=False, help_text="The code for the current journal.")

def validate_only_underscore_and_alphanumeric(value):
    """
    Only allow underscores and alphanumeric characters.
    :param value: The value to validate.
    :return:
    """
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise ValidationError(
            'Only alphanumeric characters and underscores are allowed.'
        )

class EditorialManagerTransferServiceSectionEditorForm(forms.Form):
    """
    The form for the Editorial Manager Transfer Service's Section
    """
    janeway_section_name = forms.CharField(required=True,
                                           max_length=200,
                                           label="Section Name",
                                           help_text="The name of the current section.")

    em_section_id = forms.CharField(required=False,
                                    max_length=64,
                                    label="Editorial Manager Section ID",
                                    validators=[validate_only_underscore_and_alphanumeric],
                                    help_text="Your organization's ID inside Editorial Manager for this section. May be left empty to delete. Must be all lowercase and using underscores.")

