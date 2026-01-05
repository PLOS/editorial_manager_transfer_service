"""
The models used for the production transporter.
"""
__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import uuid
from django.db import models
from plugins.editorial_manager_transfer_service.enums.report_state import ReportState
from plugins.editorial_manager_transfer_service.enums.transfer_log_message_type import TransferLogMessageType


class TransferReport(models.Model):
    """
    A model which allows us to track issues with ingest by bundling error logs by occurrence.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    report_state = models.CharField(
            max_length=3,
            choices=ReportState.choices,
            default=ReportState.IN_FLIGHT,
    )

    journal = models.ForeignKey(
            "journal.Journal",
            on_delete=models.CASCADE,
            null=True, blank=True
    )

    article = models.ForeignKey(
            "submission.Article",
            on_delete=models.CASCADE,
            null=True, blank=True
    )

    message_date_time_start = models.DateTimeField(auto_now_add=True)
    message_date_time_stop = models.DateTimeField(
            null=True, blank=True
    )
    resolved = models.BooleanField(default=False)


class TransferLogs(models.Model):
    """
    The model used for transfer logs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    message_type = models.CharField(
            max_length=2,
            choices=TransferLogMessageType.choices,
            default=TransferLogMessageType.EXPORT,
    )

    report = models.ForeignKey(
            "editorial_manager_transfer_service.TransferReport",
            on_delete=models.CASCADE,
            null=True, blank=False
    )

    journal = models.ForeignKey(
            "journal.Journal",
            on_delete=models.CASCADE,
            null=True, blank=True
    )

    article = models.ForeignKey(
            "submission.Article",
            on_delete=models.CASCADE,
            null=True, blank=True
    )

    message = models.TextField()
    message_date_time = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)

class EditorialManagerSection(models.Model):
    """
    The model used for the editorial manager section to save the variable IDs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    section = models.ForeignKey(
            "submission.Section",
            on_delete=models.CASCADE,
            null=False, blank=False
    )

    editorial_manager_section_id = models.CharField(max_length=64, null=False, blank=False)