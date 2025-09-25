"""
A file for tracking the transfer log message types.
"""
__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import django.db.models as models
from django.utils.translation import gettext_lazy as _

class TransferLogMessageType(models.TextChoices):
    EXPORT = "EX", _("Export Message")
    IMPORT = "IM", _("Import Message")