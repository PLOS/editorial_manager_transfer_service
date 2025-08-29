from django import forms


class EditorialManagerTransferServiceForm(forms.Form):
    """
    The form for the Editorial Manager Transfer Service
    """
    submission_partner_code = forms.CharField(required=False, help_text="Your organization's Submission Partner Code.")
    license_code = forms.CharField(required=False, help_text="The license code for your organization.")
    journal_code = forms.CharField(required=False, help_text="The code for the current journal.")
