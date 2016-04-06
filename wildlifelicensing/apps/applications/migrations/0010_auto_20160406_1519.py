# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-06 07:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0009_auto_20160406_0945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='status',
            field=models.CharField(choices=[('awaiting_assessment', 'Awaiting Assessment'), ('assessed', 'Assessed')], default='awaiting_assessment', max_length=20, verbose_name='Status'),
        ),
    ]
