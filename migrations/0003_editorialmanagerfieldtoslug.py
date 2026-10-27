import uuid

from django.db import migrations
from django.db.models import CharField, ForeignKey, UUIDField, deletion


class Migration(migrations.Migration):

    dependencies = [
        ('editorial_manager_transfer_service', '0002_editorialmanagersection'),
        ('submission', '0003_field'),
        ('journal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EditorialManagerFieldToSlug',
            fields=[
                ('id', UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('journal', ForeignKey(on_delete=deletion.CASCADE, to='journal.journal', null=True)),
                ('field', ForeignKey(on_delete=deletion.CASCADE, to='submission.field')),
                ('slug', CharField(max_length=40))
            ],
        ),
    ]
