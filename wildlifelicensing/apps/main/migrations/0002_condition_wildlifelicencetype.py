# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-29 03:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('licence', '0003_auto_20160323_1434'),
        ('main', '0001_make_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WildlifeLicenceType',
            fields=[
                ('licencetype_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='licence.LicenceType')),
                ('default_conditions', models.ManyToManyField(to='main.Condition')),
            ],
            options={
                'abstract': False,
            },
            bases=('licence.licencetype',),
        ),
    ]
