# Generated by Django 5.1.4 on 2025-05-16 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('company', models.CharField(blank=True, max_length=50, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
