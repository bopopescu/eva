#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from assets.models import Server as hosts
from accounts.models import CustomUser as Users
from business.models import Business 
# Create your models here.
import uuid


class Tools(models.Model):
    #"""git或svn的详细信息"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    TOOL_TYPE = [(i, i) for i in (u"GIT",u"Subversion")]
    name =models.CharField(_(u'名称'),max_length=32, choices=TOOL_TYPE)
    title = models.CharField(_(u'标题'), max_length=64, unique=True)
    address = models.CharField(_(u'地址'), max_length=128, blank=True)
    user = models.CharField(_(u'用户'), max_length=64, blank=True)
    passwd = models.CharField(_(u'密码'), max_length=64, blank=True)

    class Meta:
        verbose_name = u'版本管理工具'
        verbose_name_plural = verbose_name
    def __unicode__(self):
        return self.title


class Confile(models.Model):
    #"""关联业务的版本发布需要的一些信息"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(_(u'发布标题'), max_length=64, unique=True)
    ENVIRONMENT_SELECT = (
    ("production",u"线上环境"),
    ("test",u"测试环境"),
    ("huidu",u"灰度环境"),
    )
    environment = models.CharField(max_length=64, choices=ENVIRONMENT_SELECT,verbose_name=u'部署环境')
    tool = models.ForeignKey(Tools,on_delete=models.SET_NULL,related_name='first_tool', blank=True,null=True,verbose_name=u'代码仓库1')
    tool_two = models.ForeignKey(Tools,on_delete=models.SET_NULL,related_name='second_tool', blank=True,null=True,verbose_name=u'代码仓库2')
    tool_three = models.ForeignKey(Tools,on_delete=models.SET_NULL,related_name='third_tool', blank=True,null=True,verbose_name=u'代码仓库3')
    tool_tail = models.CharField(max_length=64,blank=True,null=True,verbose_name=u'仓库1尾巴')
    tool_tail_two = models.CharField(max_length=64,blank=True,null=True,verbose_name=u'仓库2尾巴')
    tool_tail_three = models.CharField(max_length=64,blank=True,null=True,verbose_name=u'仓库3尾巴')
    business = models.ForeignKey(Business,verbose_name=u'关联业务', blank=True,null=True)
    localhost_dir = models.CharField(_(u'检出目录1'), max_length=128, blank=True)
    localhost_dir_two = models.CharField(_(u'检出目录2'), max_length=128, blank=True)
    localhost_dir_three = models.CharField(_(u'检出目录3'), max_length=128, blank=True)
    specific = models.CharField(_(u'指定文件'),max_length=128,blank=True)
    exclude = models.TextField(_(u'排除文件'),blank=True)
    webroot_user = models.CharField(_(u'web用户'), max_length=32,default='www')
    webroot = models.CharField(_(u'web目录'), max_length=128)
    relaese_dir = models.CharField(_(u'发布版本库'), max_length=64)
    max_number = models.IntegerField(_(u'保留版本数'), blank=True,default=10)
    server_list = models.TextField(_(u'服务器列表'), blank=True)
    pre_deploy = models.TextField(_(u'部署前动作'), blank=True)
    post_deploy = models.TextField(_(u'部署后动作'), blank=True)
    pre_release = models.TextField(_(u'版本拉取前动作'), blank=True)
    post_release = models.TextField(_(u'版本拉取后动作'), blank=True)
    status = models.BooleanField(default=True,verbose_name=u'是否启用')


    class Meta:
        verbose_name = u'版本发布属性'
        verbose_name_plural = verbose_name
    def __unicode__(self):
        return self.name



class deploy(models.Model):
    #"""申请发布表单，用户只需要填写名称，分支与版本"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    ctime = models.DateTimeField(verbose_name=u'创建时间',blank=True, auto_now=True)
    name = models.CharField(_(u'发布名称'),max_length=64)
    sit_id = models.CharField(_(u'发布代号'),max_length=64,blank=True)
    branches = models.CharField(_(u'分支'),max_length=64,blank=True)
    release = models.CharField(_(u'commit_id'),max_length=64,blank=True)
    release_two = models.CharField(_(u'commit_id_two'),max_length=64,blank=True)
    release_three = models.CharField(_(u'commit_id_three'),max_length=64,blank=True)
    executive_user = models.ForeignKey(Users,verbose_name=u'用户')
    confile = models.ForeignKey('Confile',verbose_name=u'发布项目配置')
    CONFILE_CHECK = [(i, i) for i in (u'已通过',u'未通过')]
    check_conf = models.CharField(_(u'审核状态'),max_length=32,choices=CONFILE_CHECK,blank=True)
    STATUS_CHECK = [(i, i) for i in (u'已发布',u'未发布',u'已回滚')]
    status = models.CharField(_(u'状态'),max_length=32,choices=STATUS_CHECK,default=u'未发布',blank=True)
    tag = models.CharField(_(u'主库版本号'),max_length=64,blank=True)
    tag_two = models.CharField(_(u'副库版本号'),max_length=64,blank=True)
    tag_three = models.CharField(_(u'叁库版本号'),max_length=64,blank=True)
    memo = models.TextField(_(u'发布原因'))
    execution_time = models.IntegerField(_(u'发布时间'),default=0)
    exist = models.BooleanField(default='False')



    class Meta:
        verbose_name = u'发布申请单'
        verbose_name_plural = verbose_name
    def __unicode__(self):
        return self.name




class scriptrepo(models.Model):
    """运维发布更新"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(_(u'发布名称'),max_length=64)
    command = models.CharField(_(u'命令'),max_length=128)
    server_ip = models.GenericIPAddressField(_(u'脚本服务器'),max_length=128)
    customargs = models.TextField(_(u'自定义参数'),null=True)
    custom_state = models.BooleanField(_(u'启用自定义参数'),default=False)
    memo = models.TextField(_(u'介绍备注'),null=True)





class scriptlog(models.Model):
    """脚本发布更新日志记录"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user =  models.ForeignKey(Users,verbose_name=u'用户')
    name = models.CharField(_(u'名称'),max_length=128,blank=True)
    memo = models.TextField(_(u'发布原因'),blank=True)
    command = models.CharField(_(u'命令'),max_length=128)
    result = models.TextField(_(u'命令输出'),max_length=128)
    create_time = models.DateTimeField(auto_now_add=True)
    sort_time = models.IntegerField(default=0)
    scriptdeploy = models.ForeignKey('scriptdeploy',verbose_name=u'用户',blank=True,null=True)


class scriptdeploy(models.Model):
    """开发自行发布更新"""
    STATUS_CHECK = [(i, i) for i in (u'已更新',u'未更新',u'已发布',u'未发布',u'已回滚')]
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(_(u'发布名称'),max_length=64,blank=True)
    sit_id = models.CharField(_(u'发布代号'),max_length=12,blank=True)
    release = models.CharField(_(u'参数1'),max_length=32)
    release_two = models.CharField(_(u'参数2'),max_length=32,blank=True)
    release_three = models.CharField(_(u'参数3'),max_length=32,blank=True)
    memo = models.TextField(_(u'发布原因'))
    ctime = models.DateTimeField(verbose_name=u'申请时间',blank=True, auto_now=True)
    execution_time = models.IntegerField(_(u'发布时间'),default=0)
    executive_user = models.ForeignKey(Users,verbose_name=u'用户')
    check_conf = models.BooleanField(default=True)
    status = models.CharField(_(u'状态'),max_length=32,choices=STATUS_CHECK,default=u'未更新',blank=True)

class AUser(models.Model):
    """审核人员"""
    AUDIT_CLASSIFY  = (
    ("website_normal",u"现金网正常审核"),
    ("website_urgent",u"现金网紧急审核"),
    )
    name = models.CharField(_(u'名称'),max_length=25,choices=AUDIT_CLASSIFY)
    user = models.ManyToManyField(Users)
    def __unicode__(self):
        return self.name

class gengxin_code(models.Model):
    CLASSIFY_CHOICE = (
        ('huidu', u'灰度'),
        ('online', u'生产'),
        ('test', u'测试'),
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(_(u'名称'),max_length=45,blank=True,default="1001")
    classify =  models.CharField(_(u'类型'),max_length=64,choices=CLASSIFY_CHOICE,default="类别")
    business = models.ForeignKey(Business,verbose_name=u'关联业务',null=True,blank=True)
    remoteip = models.TextField(_(u'服务器ip'),null=True,blank=True,default='119.9.81.134')
    phone_site = models.BooleanField(_(u'手机端是否发布'),default=False)

    remotedir = models.CharField(_(u'线上目录'),null=True,blank=True,max_length=45,default='/data/wwwroot/1001')
    exclude = models.TextField(_(u'排除文件'),null=True,blank=True,default='Logs/')
    rsync_command = models.TextField(_(u'推送前命令'),null=True,blank=True)
    last_command = models.TextField(_(u'生效前命令'),null=True,blank=True)

    isurgent = models.BooleanField(_(u'紧急更新'),default=False)
    ischeck = models.BooleanField(_(u'是否审核'),default=False)
    period_time = models.CharField(_(u'更新时段'),null=True,blank=True,max_length=45)
    deploy_time = models.IntegerField(_(u'更新频率'),default=0)
    urgent_user = models.ForeignKey(AUser,verbose_name=u'紧急审核人', blank=True,null=True,on_delete=models.SET_NULL, related_name='urg')
    audit_user = models.ForeignKey(AUser,verbose_name=u'正常审核人', blank=True,null=True,on_delete=models.SET_NULL, related_name='aud')
    front_domain = models.TextField(_(u'前端域名'),null=True,blank=True,default='1001.s1119.com')
    agent_domain = models.TextField(_(u'代理后台域名'),null=True,blank=True,default='ag1001.s1119.com')
    backend_domain = models.TextField(_(u'后台域名'),null=True,blank=True,default='ds168.xxx.com\r\nds168.yyy.com')

    class Meta:
        ordering = ['name']
        verbose_name = u'gengxin_code'
        verbose_name_plural = verbose_name
    def __unicode__(self):
        return self.name




class gengxin_deploy(models.Model):
    #"""申请发布表单，用户只需要填写名称，分支与版本"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(_(u'名称'),max_length=64)
    code_conf = models.ForeignKey(gengxin_code,verbose_name=u'配置信息',null=True,blank=True,related_name='deploy')
    executive_user = models.ForeignKey(Users,verbose_name=u'用户')
    status = models.CharField(_(u'进行状态'),max_length=32,blank=True)
    audit_status = models.TextField(_(u'审核状态'),null=True,blank=True)
    siteid = models.CharField(max_length=10,null=True,blank=True)
    method = models.CharField(max_length=10,null=True,blank=True)
    web_reversion = models.CharField(max_length=40,null=True,blank=True)
    pub_reversion = models.CharField(max_length=40,null=True,blank=True)
    con_reversion = models.CharField(max_length=40,null=True,blank=True)
    memo = models.TextField(_(u'发布原因'),null=True,blank=True)
    execution_time = models.CharField(_(u'完成时间'),null=True,blank=True,max_length=64)
    ctime = models.DateTimeField(auto_now_add=True)
    exist = models.BooleanField(_(u'是否结束'),default=False)
    class Meta:
        ordering = ['-ctime']
