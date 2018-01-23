# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2018-01-22 08:38
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gitfabu', '0002_auto_20180122_1611'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Allow_list', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='white_conf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('KG-JDC', 'KG\u7ecf\u5178\u5f69'), ('MN-Backend', '\u86ee\u725b\u540e\u53f0'), ('MONEY-Backend', '\u73b0\u91d1\u7f51\u540e\u53f0')], max_length=25, unique=True, verbose_name='\u767d\u540d\u5355\u914d\u7f6e')),
                ('servers', models.TextField(verbose_name='\u670d\u52a1\u5668\u5730\u5740')),
                ('file_path', models.CharField(max_length=100, verbose_name='\u6587\u4ef6\u7edd\u5bf9\u8def\u5f84')),
                ('is_reload', models.BooleanField(default=False, verbose_name='\u662f\u5426\u91cd\u542f')),
            ],
        ),
        migrations.CreateModel(
            name='white_list',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host_key', models.CharField(choices=[('allow', '\u5141\u8bb8'), ('deny', '\u62d2\u7edd')], max_length=10, verbose_name='\u767d\u540d\u5355key')),
                ('host_ip', models.CharField(max_length=15, verbose_name='\u767d\u540d\u5355value')),
                ('git_deploy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='white', to='gitfabu.git_deploy')),
                ('white_conf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Allow_list.white_conf')),
            ],
        ),
        migrations.AlterField(
            model_name='iptables',
            name='i_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='iptables',
            name='i_comment',
            field=models.CharField(blank=True, choices=[('\u6fb3\u95e8\u7f8e\u9ad8\u6885', '\u6fb3\u95e8\u7f8e\u9ad8\u6885'), ('\u65b0\u8461\u4eac', '\u65b0\u8461\u4eac'), ('\u8461\u4eac\u56fd\u9645', '\u8461\u4eac\u56fd\u9645'), ('\u5927\u53d1\u9177\u5ba2', '\u5927\u53d1\u9177\u5ba2'), ('\u6fb3\u95e8\u56fd\u9645', '\u6fb3\u95e8\u56fd\u9645'), ('\u76db\u4e16\u56fd\u9645', '\u76db\u4e16\u56fd\u9645'), ('\u6613\u53d1', '\u6613\u53d1'), ('\u83f2\u5f8b\u5bbe', '\u83f2\u5f8b\u5bbe'), ('\u8bda\u4fe1', '\u8bda\u4fe1'), ('\u535a\u72d7\u5a31\u4e50\u57ce', '\u535a\u72d7\u5a31\u4e50\u57ce'), ('\u5b88\u4fe1\u5a31\u4e50\u57ce', '\u5b88\u4fe1\u5a31\u4e50\u57ce'), ('\u6fb3\u95e8\u5a01\u5c3c\u65af\u4eba', '\u6fb3\u95e8\u5a01\u5c3c\u65af\u4eba'), ('\u91d1\u5b9d\u535a', '\u91d1\u5b9d\u535a')], max_length=50),
        ),
    ]