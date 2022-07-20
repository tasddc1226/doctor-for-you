# Generated by Django 4.0.6 on 2022-07-20 00:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mydoctor', '0009_rename_launch_from_weekdaytime_lunch_from_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CareRequestList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_time', models.DateField(verbose_name='희망 진료 시각')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='예약 요청 시각')),
                ('expire_time', models.DateTimeField(verbose_name='요청 만료 시각')),
                ('is_booked', models.BooleanField(default=True, verbose_name='진료 요청 수락 여부')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mydoctor.doctor', verbose_name='의사 id')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mydoctor.patient', verbose_name='환자 id')),
            ],
            options={
                'db_table': 'care',
            },
        ),
    ]