# Generated by Django 5.1.6 on 2025-03-08 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0017_guide_alloted_data'),
    ]

    operations = [
        migrations.RenameField(
            model_name='guide_alloted_data',
            old_name='nmae',
            new_name='name',
        ),
    ]
