from django.core.exceptions import FieldDoesNotExist
from django.db import migrations

from ..models import EditorialManagerFieldToSlug


def populate_field_to_slug_mapping(apps, schema_editor):
    Field = apps.get_model("submission", "Field")
    fields = Field.objects.all()

    for field in fields:
        try:
            if field.slug is not None and field.journal is not None:
                field_to_slug_mapping, created = EditorialManagerFieldToSlug.objects.get_or_create(
                    journal_id=field.journal.id, field_id=field.id, slug=field.slug
                )
        except FieldDoesNotExist:
            # Migration being run after slug column deleted from codebase, therefore this is a no-op
            return

class Migration(migrations.Migration):

    dependencies = [
        ('editorial_manager_transfer_service', '0003_editorialmanagerfieldtoslug'),
        ('submission', '0003_field'),
    ]

    operations = [
        migrations.RunPython(populate_field_to_slug_mapping)
    ]
