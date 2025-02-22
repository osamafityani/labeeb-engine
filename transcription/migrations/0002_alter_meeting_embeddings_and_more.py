# Generated by Django 5.1.4 on 2025-02-22 10:26

import pgvector.django.vector
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transcription', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='embeddings',
            field=pgvector.django.vector.VectorField(blank=True, dimensions=1536, null=True),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='transcription_file',
            field=models.FileField(blank=True, null=True, upload_to='uploads/'),
        ),
    ]
