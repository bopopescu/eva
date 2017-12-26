# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2017-12-26 06:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60, verbose_name='\u6807\u9898')),
                ('author', models.CharField(max_length=20, verbose_name='\u4f5c\u8005')),
                ('body', models.TextField(verbose_name='\u6587\u7ae0\u5185\u5bb9')),
                ('change_date', models.CharField(default='2017-01-01 12:00:00', max_length=20, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='\u65f6\u95f4')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='\u7c7b\u540d')),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='opswiki.Category', verbose_name='\u5206\u7c7b'),
        ),
    ]
