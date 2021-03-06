# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-10-28 17:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0003_auto_20180417_1932'),
        ('audit', '0003_auto_20180915_1440'),
    ]

    operations = [
        migrations.CreateModel(
            name='sql_DangousKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dkey', models.CharField(blank=True, max_length=128, verbose_name='\u5173\u952e\u5b57')),
            ],
        ),
        migrations.RenameField(
            model_name='sql_apply',
            old_name='isaudit',
            new_name='dangerous',
        ),
        migrations.RenameField(
            model_name='sql_apply',
            old_name='file_name',
            new_name='filename',
        ),
        migrations.RenameField(
            model_name='sql_apply',
            old_name='md5v',
            new_name='md5user',
        ),
        migrations.RenameField(
            model_name='sql_apply',
            old_name='file_path',
            new_name='savename',
        ),
        migrations.RemoveField(
            model_name='sql_apply',
            name='database',
        ),
        migrations.RemoveField(
            model_name='sql_apply',
            name='name',
        ),
        migrations.RemoveField(
            model_name='sql_apply',
            name='sql_type',
        ),
        migrations.RemoveField(
            model_name='sql_apply',
            name='statement',
        ),
        migrations.RemoveField(
            model_name='sql_apply',
            name='status',
        ),
        migrations.RemoveField(
            model_name='sql_conf',
            name='cluster',
        ),
        migrations.RemoveField(
            model_name='sql_conf',
            name='local_vip',
        ),
        migrations.RemoveField(
            model_name='sql_conf',
            name='master_node',
        ),
        migrations.RemoveField(
            model_name='sql_conf',
            name='pub_vip',
        ),
        migrations.RemoveField(
            model_name='sql_conf',
            name='slave_node',
        ),
        migrations.RemoveField(
            model_name='sql_conf',
            name='vip_port',
        ),
        migrations.AddField(
            model_name='sql_apply',
            name='keyword',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sql_apply',
            name='md5value',
            field=models.CharField(blank=True, max_length=45),
        ),
        migrations.AddField(
            model_name='sql_apply',
            name='passed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sql_apply',
            name='review',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sql_apply',
            name='sqlconf',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sqlfile', to='audit.sql_conf'),
        ),
        migrations.AddField(
            model_name='sql_apply',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='\u7533\u8bf7\u4eba'),
        ),
        migrations.AddField(
            model_name='sql_conf',
            name='apply_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='apply_sql', to='accounts.department_Mode'),
        ),
        migrations.AddField(
            model_name='sql_conf',
            name='group_ops',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ops_audit', to='accounts.department_Mode'),
        ),
        migrations.AddField(
            model_name='sql_conf',
            name='host',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='sql_conf',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sql_conf',
            name='workdir',
            field=models.CharField(default='/data/sqlfile/', max_length=64),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sql_conf',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_sql', to='accounts.department_Mode'),
        ),
    ]
