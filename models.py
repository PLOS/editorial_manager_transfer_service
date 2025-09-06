"""
The models used for the production transporter.
"""
__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

from django.db import models
from plugins.editorial_manager_transfer_service.enums.transfer_log_message_type import TransferLogMessageType


class TransferLogs(models.Model):
    """
    The model used for transfer logs.
    """
    message_type = models.CharField(
            max_length=2,
            choices=TransferLogMessageType.choices,
            default=TransferLogMessageType.EXPORT,
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