# Generated by Django 4.0.6 on 2022-07-19 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mydoctor', '0003_alter_weekdaytime_table_alter_weekendtime_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='non_paid',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='비급여진료과목'),
        ),
    ]
