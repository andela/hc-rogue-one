# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-05-16 08:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0005_auto_20180516_0721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='frequentlyaskedquestion',
            name='status',
            field=models.CharField(choices=[('h', 'hidden'), ('s', 'showing')], default='h', max_length=1),
        ),
    ]
