# Generated by Django 5.0.6 on 2024-07-07 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_organisation'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
