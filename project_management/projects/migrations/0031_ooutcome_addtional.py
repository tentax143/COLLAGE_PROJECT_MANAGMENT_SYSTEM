# Generated by Django 5.1.6 on 2025-03-25 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0030_project_achieved_project_outcome_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ooutcome_addtional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reg_no', models.CharField(max_length=20)),
                ('batch', models.CharField(max_length=200)),
                ('semester', models.CharField(max_length=200)),
                ('guide_name', models.CharField(max_length=200)),
                ('outcome', models.CharField(max_length=200)),
                ('web_url', models.CharField(max_length=200)),
                ('journal_name', models.CharField(max_length=200)),
                ('volume', models.CharField(max_length=200)),
                ('page_no', models.CharField(max_length=200)),
                ('doi', models.CharField(max_length=200)),
                ('impact_factor', models.CharField(max_length=200)),
            ],
        ),
    ]
