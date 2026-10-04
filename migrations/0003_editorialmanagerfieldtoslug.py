import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editorial_manager_transfer_service', '0002_editorialmanagersection'),
    ]

    operations = [
        migrations.CreateModel(
            name='EditorialManagerFieldToSlug',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('journal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='submission.journal')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='submission.field')),
                ('slug', models.CharField(max_length=40))
            ],
        ),
    ]
