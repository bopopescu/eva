#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import render

from gitfabu.models import git_deploy,my_request_task,git_deploy_logs,git_deploy_audit,git_task_audit,git_coderepo,git_ops_configuration,git_code_update
from business.models import Business,DomainName
from assets.models import Server
from accounts.models import department_Mode
from gitfabu.forms import git_deploy_audit_from
# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from gitfabu.tasks import git_fabu_task,git_moneyweb_deploy,git_update_task,git_update_public_task
from django.contrib.auth.decorators import login_required
import time
from api.git_api import Repo
from gitfabu.audit_api import task_distributing,check_group_audit,onekey_access
import telegram
bot = telegram.Bot(token='460040810:AAG4NYR9TMwcscrxg0uXLJdsDlP3a6XohJo')


def mytasknums(request):
    nums = {}
    try:
        mdata = len(my_request_task.objects.filter(initiator=request.user,isend=False,loss_efficacy=False))
    except:
        mdata = 0
    nums['myrequesttasks']=mdata
    try:
        odata = len(git_task_audit.objects.filter(auditor=request.user,isaudit=False,loss_efficacy=False))
    except:
        odata = 0
    nums['myaudittasks']=odata
    return nums

@login_required
def conf_list(request):
    data_huidu = git_deploy.objects.filter(platform="现金网",classify="huidu",isops=True,islog=True)
    data_test = git_deploy.objects.filter(platform="现金网",classify="test",islog=True)
    data_online = git_deploy.objects.filter(platform="现金网",classify="online",isops=True,islog=True)
    alone = git_deploy.objects.filter(platform="单个项目",classify="online",isops=True,islog=True)
    return render(request,'gitfabu/conf_list.html',locals())

@login_required
def version_list(request,uuid):
    data = git_deploy.objects.get(pk=uuid)
    if data.old_reversion:
        old_reversion = data.old_reversion.split('\r\n')
    else:
        old_reversion = []
    return render(request,'gitfabu/version_list.html',locals())

def deploy_domains(request):
    classify = request.GET.get('classify')
    siteid = request.GET.get('siteid')
    platform = request.GET.get('platform')
    business = Business.objects.get(platform=platform,status=0,nic_name=siteid)
    f = business.domain.filter(use=0,classify=classify)
    a = business.domain.filter(use=1,classify=classify)
    b = business.domain.filter(use=2,classify=classify)
    webtext = "\n".join([i.name for i in f if i])
    agtext = "\n".join([i.name for i in a if i])
    ds168text = "\n".join([i.name for i in b if i])
    return JsonResponse({"webtext":webtext,"agtext":agtext,"ds168text":ds168text},safe=False)

@login_required
def conf_add_alone_project(request):
    """单独项目添加，需要配置服务器，git地址，线上目录"""
    project = "现金网"
    export_dir = "/data/onlyproject/online/export/"
    errors = []
    if request.method == "POST":
        name = request.POST.get("name")
        memo = request.POST.get("memo")
        git_branch = request.POST.get("git_branch")
        git_commit = request.POST.get("git_commit")
        repo = request.POST.get("repo")

        if not "http" in repo: errors.append("git地址有错误！缺少http关键字")

        git_export = export_dir+name

        remoteip = request.POST.get("remoteip")
        for i in remoteip.split('\r\n'):
            try:
                Server.objects.get(ssh_host=i)
            except:
                errors.append("CMDB中无此IP：%s"% i)

        remotedir = request.POST.get("remotedir")
        owner = request.POST.get("owner")
        exclude = request.POST.get("exclude")
        rsync_command = request.POST.get("rsync_command")
        last_command = request.POST.get("last_command")

        #if git_coderepo.objects.filter(title=name,classify="online",platform="单个项目"): errors.append("已有相关项目git地址配置,请检查是否有重名项目！")
        #if git_ops_configuration.objects.filter(name=name,classify="online",platform="单个项目"): errors.append("已有相关项目服务器配置,请检查是否有重名项目！")

        if errors: return render(request,'gitfabu/add_alone_project.html',locals())

        #先存储服务器相关配置
        obj,server_data = git_ops_configuration.objects.get_or_create(name=name,classify="online",platform="单个项目",defaults={'remoteip':remoteip,'remotedir':remotedir,'owner':owner,"exclude":exclude,"rsync_command":rsync_command,"last_command":last_command})
        if obj:
            server_data = obj
        else:
            server_data = server_data
        #再存储git相关配置
        obj,repo_data = git_coderepo.objects.get_or_create(title=name,classify="online",platform="单个项目",defaults={"address":repo,"user":"fabu","passwd":"DSyunweibu110110","branch":git_branch,"reversion":git_commit})
        #先创建git_deploy实例
        deploy_obj,deploy = git_deploy.objects.get_or_create(name=name,platform="单个项目",classify="online",server=server_data,isdev=True,isops=True)
        if obj:
            data = deploy_obj
        else:
            data = deploy
        #最后创建审核任务，分发审核,因为运维直接参与配置所以不需要审核
        mydata = my_request_task(name=name+"_线上发布",table_name="git_deploy",uuid=data.id,initiator=request.user,memo=memo,status="发布中")
        mydata.save()
        reslut = git_fabu_task.delay(data.id,mydata.id)
        return HttpResponseRedirect('/fabu/mytask/')
    return render(request,'gitfabu/add_alone_project.html',locals())

@login_required
def conf_add_java_project(request):
    """单独项目添加，需要配置服务器，git地址，线上目录"""
    project = "蛮牛JAVA"
    export_dir = "/data/javaproject/online/export/"
    errors = []
    if request.method == "POST":
        name = request.POST.get("name")
        memo = request.POST.get("memo")
        git_branch = request.POST.get("git_branch")
        git_commit = request.POST.get("git_commit")
        repo = request.POST.get("repo")

        if not "http" in repo: errors.append("git地址有错误！缺少http关键字")

        git_export = export_dir+name

        remoteip = request.POST.get("remoteip")
        for i in remoteip.split('\r\n'):
            try:
                Server.objects.get(ssh_host=i)
            except:
                errors.append("CMDB中无此IP：%s"% i)

        remotedir = request.POST.get("remotedir")
        owner = request.POST.get("owner")
        exclude = request.POST.get("exclude")
        rsync_command = request.POST.get("rsync_command")
        last_command = request.POST.get("last_command")

        #if git_coderepo.objects.filter(title=name,classify="online",platform="JAVA项目"): errors.append("已有相关项目git地址配置,请检查是否有重名项目！")
        #if git_ops_configuration.objects.filter(name=name,classify="online",platform="JAVA项目"): errors.append("已有相关项目服务器配置,请检查是否有重名项目！")

        if errors: return render(request,'gitfabu/add_alone_project.html',locals())

        #先存储服务器相关配置
        obj,server_data = git_ops_configuration.objects.get_or_create(name=name,classify="online",platform="JAVA项目",defaults={'remoteip':remoteip,'remotedir':remotedir,'owner':owner,"exclude":exclude,"rsync_command":rsync_command,"last_command":last_command})
        if obj:
            server_data = obj
        else:
            server_data = server_data
        #再存储git相关配置
        obj,repo_data = git_coderepo.objects.get_or_create(title=name,classify="online",platform="JAVA项目",defaults={"address":repo,"user":"fabu","passwd":"DSyunweibu110110","branch":git_branch,"reversion":git_commit})
        #先创建git_deploy实例
        deploy_obj,deploy = git_deploy.objects.get_or_create(name=name,platform="JAVA项目",classify="online",server=server_data,isdev=True,isops=True)
        if obj:
            data = deploy_obj
        else:
            data = deploy
        #最后创建审核任务，分发审核,因为运维直接参与配置所以不需要审核
        mydata = my_request_task(name=name+"_线上发布",table_name="git_deploy",uuid=data.id,initiator=request.user,memo=memo,status="发布中")
        mydata.save()
        reslut = git_fabu_task.delay(data.id,mydata.id)
        return HttpResponseRedirect('/fabu/mytask/')
    return render(request,'gitfabu/add_alone_project.html',locals())


@login_required
def conf_add(request,env):
    errors = []
    if "money" in env:
        platform = "现金网"
        conf_domain = True
    elif "manniu" in env:
        platform = "蛮牛"
        conf_domain = True
    elif "java" in env:
        platform = "JAVA项目"
        conf_domain = False
    else:
        platform = "单个项目"
        conf_domain = False
    if "huidu" in env: 
        dname = platform + "_灰度发布"
        envir = "huidu"
        envname = "灰度"
    if "online" in env: 
        dname = platform + "_线上发布"
        envir = "online"
        envname = "生产"
    if "test" in env: 
        dname = platform + "_测试发布"
        envir = "test"
        envname = "测试"
    deploy = [i.name for i in git_deploy.objects.filter(platform=platform,classify=envir,isops=True,islog=True)]
    busi = [] #只显示没有发布过的项目
    for i in Business.objects.filter(platform=platform,status=0):
        if i.nic_name not in deploy:
            busi.append(i)

    if request.method == 'POST':
        name = request.POST.get('business') #所有发布的项目使用business中的nic_name当作名称
        gg = git_deploy.objects.filter(name=name,platform=platform,classify=envir,isops=True,islog=True)

        if len(gg) > 0:
            errors.append("项目以存在，请联系运维处理")
        business = Business.objects.get(nic_name=name)

        #配置服务器地址，没有配置会报错，所以使用try
        try:
            if platform == "现金网" or platform == "蛮牛":
                server = git_ops_configuration.objects.get(name="源站",platform=platform,classify=envir)
            else:
                server = git_ops_configuration.objects.get(name=name,platform=platform,classify=envir)
        except IndexError:
            errors.append("没有配置-%s-%s-%s-服务器地址"% (platform,business.name,envir))

        #检测域名正确性，测试环境不会检查ag与backend域名,发布Huidu的时候需要填写后台域名，发布线上的时候需要填写前台与ag域名
        #蛮牛现金网副网不检测域名后台
        #C网
        if platform == "现金网" or platform == "蛮牛":
            f_domainname = DomainName.objects.filter(use=0,business=business,classify=envir)
            a_domainname = DomainName.objects.filter(use=1,business=business,classify=envir)
            b_domainname = DomainName.objects.filter(use=2,business=business,classify=envir)
            if f_domainname:
                f_domainname = [i.name for i in f_domainname]
            else:
                errors.append("没有给出前端域名,请联系产品添加域名")
            if envir != "test":
                if a_domainname:
                    a_domainname = [i.name for i in a_domainname]
                else:
                    errors.append("没有给出ag域名,请联系产品添加域名")
                if b_domainname:
                    b_domainname = [i.name for i in b_domainname]
                else:
                    errors.append("没有给出后台域名,请联系产品添加域名")

        if errors: return render(request,'gitfabu/conf_add.html',locals())

        #配置git地址，如果没有找到web/1001.git类似的私有仓库，则创建保存
        money_git = "http://git.dtops.cc/"
        username = "fabu"    #写死的，以后会是一个bug
        password = "DSyunweibu110110"
        if platform == "现金网":  #注意：只有现金网和蛮牛的web项目发布时才会创建git地址，其他的单独项目和JAVA项目应该手动添加git的相关信息
            web = money_git+"web/%s.git"% name
            obj,created = git_coderepo.objects.get_or_create(platform=platform,classify=envir,ispublic=False,title=name,defaults={'address':web,'user':username,'passwd':password},)
            php_pc,php_pc_repo = git_coderepo.objects.get_or_create(platform=platform,classify=envir,ispublic=True,title="php_pc",defaults={'address':money_git+"php/1000_public_php.git",'user':username,'passwd':password})
            php_mob,php_mob_repo = git_coderepo.objects.get_or_create(platform=platform,classify=envir,ispublic=True,title="php_mobile",defaults={'address':money_git+"php/1000m_public_php.git",'user':username,'passwd':password})
            js_pc,js_pc_repo = git_coderepo.objects.get_or_create(platform=platform,classify=envir,ispublic=True,title="js_pc",defaults={'address':money_git+"web/1000_public_js.git",'user':username,'passwd':password})
            js_mob,js_mob_repo = git_coderepo.objects.get_or_create(platform=platform,classify=envir,ispublic=True,title="js_mobile",defaults={'address':money_git+"web/1000m_public_js.git",'user':username,'passwd':password})
            configobj,configrepo = git_coderepo.objects.get_or_create(platform=platform,classify=envir,ispublic=False,title=name+"_config",defaults={'address':money_git+"config/"+name+".git",'user':username,'passwd':password})
        elif platform == "蛮牛":
            web = money_git+"jack/%s.git"% name
            obj,created = git_coderepo.objects.get_or_create(platform=platform,classify=envir,ispublic=False,title=name,defaults={'address':web,'user':username,'passwd':password},)
            jsobj,jsrepo = git_coderepo.objects.get_or_create(platform=platform,classify=envir,ispublic=True,title="mn_js",defaults={'address':money_git+"jack/mn-web-public.git",'user':username,'passwd':password})
            phpobj,phprepo = git_coderepo.objects.get_or_create(platform=platform,classify=envir,ispublic=True,title="mn_php",defaults={'address':money_git+"harrisdt15f/wcphpsec.git",'user':username,'passwd':password})
            configobj,configrepo = git_coderepo.objects.get_or_create(platform=platform,classify=envir,ispublic=True,title="mn_config",defaults={'address':money_git+"harrisdt15f/phpcofig.git",'user':username,'passwd':password})


        ddata,created = git_deploy.objects.get_or_create(name=name,platform=platform,classify=envir,business=business,defaults={'conf_domain':conf_domain,'server':server,'usepub':conf_domain,'isdev':True},)

        #保存配置域名
        # if platform == "现金网" or platform == "蛮牛":
        #     for i in f_domainname:
        #         obj,created = DomainName.objects.get_or_create(name=i,use='0',business=business,classify=envir,defaults={'state':'0','supplier':"工程"},)
        #     if envir != "test":
        #         for i in a_domainname:
        #             obj,created = DomainName.objects.get_or_create(name=i,use='1',business=business,classify=envir,defaults={'state':'0','supplier':"工程"},)
        #         for i in b_domainname:
        #             obj,created = DomainName.objects.get_or_create(name=i,use='2',business=business,classify=envir,defaults={'state':'0','supplier':"工程"},)


        #分配审核任务
        task_name = "%s--%s"% (dname,name)
        memo = "%s,%s环境,%s发布"% (platform,envname,name)
        mydata = my_request_task(name=task_name,table_name="git_deploy",uuid=ddata.id,initiator=request.user,memo=memo,status="审核中")
        mydata.save()
        if envir == 'test':  #测试环境直接发布，其他环境需要分发审核任务
            mydata.status = "发布中"
            mydata.save()
            reslut = git_fabu_task.delay(ddata.id,mydata.id)
        else:
            auditor = git_deploy_audit.objects.get(platform=platform,classify=envir,name="发布")
            task_distributing(mydata.id,auditor.id)
    return render(request,'gitfabu/conf_add.html',locals())

@login_required
def my_request_task_list(request):
    if request.user.username == "wuhf":
        data = my_request_task.objects.filter(isend=False,loss_efficacy=False).order_by('-create_date')
    else:
        data = my_request_task.objects.filter(initiator=request.user,loss_efficacy=False).order_by('-create_date')[0:50]
    # data = my_request_task.objects.filter(initiator=request.user,loss_efficacy=True).order_by('-create_date')[0:100]
    return render(request,'gitfabu/my_request_task.html',locals())

@login_required
def others_request_task_list(request):
    if request.user.username == "wuhf":
        # data = []
        # ll = []
        # sdata = my_request_task.objects.filter(isend=False,loss_efficacy=False)
        # for i in sdata:
        #     for j in i.reqt.all():
        #         data.append(j)
        data = git_task_audit.objects.filter(isaudit=False,loss_efficacy=False)
    else:
        data = git_task_audit.objects.filter(auditor=request.user).order_by('-create_date')[0:50]
    data = git_task_audit.objects.filter(auditor=request.user,loss_efficacy=False).order_by('-create_date')[0:50]
    return render(request,'gitfabu/others_request_task.html',locals())

@login_required
def cancel_my_task(request,uuid):
    data = my_request_task.objects.get(id=uuid)
    data.loss_efficacy=True
    data.status="已停止"
    df = eval(data.table_name).objects.get(pk=data.uuid)
    if data.table_name == "git_code_update":
        if df.code_conf: #单个更新任务，删除任务，解锁项目
            df.code_conf.islock = False
            df.code_conf.save()
        else:
            if "现金网" in df.name: platform = "现金网"
            if "蛮牛" in df.name: platform = "蛮牛"
            if "huidu" in df.name: classify = "huidu"
            if "online" in df.name: classify = "online"
            if "test" in df.name: classify = "test"
            git_deploy.objects.filter(platform=platform,classify=classify,islog=True,usepub=True).update(islock=False)
    df.delete() #删除任务
    data.reqt.all().update(loss_efficacy=True) #停止相关的审核任务
    data.save()  #停止此次申请任务，还应当将锁住的项目解锁
    return JsonResponse({'res':"已经终止申请"},safe=False)

@login_required
def my_task_details(request,uuid):
    data = my_request_task.objects.get(id=uuid)
    print data.loss_efficacy
    others_data = data.reqt.all().order_by('audit_time') #分发的审核任务
    groups = list(set([i.audit_group_id for i in others_data if i])) #拿到审核组的ID
    groups = [department_Mode.objects.get(id=i) for i in groups] #拿到审核组的对象集合
    res = {} 
    for i in groups: #组遍历，组织一个dist：{"GroupName":{"member":[组员审核信息],"date":"","time":"","status":""}}
        L = []
        status = "该组未审核"
        others_data = data.reqt.filter(audit_group_id=str(i.id)).order_by('audit_time')

        pass_data = data.reqt.filter(audit_group_id=str(i.id),isaudit=True,ispass=True)
        if pass_data: status = "该组已通过"
        nopass_data = data.reqt.filter(audit_group_id=str(i.id),isaudit=True,ispass=False)
        if nopass_data: status = "该组未通过"

        for j in others_data:
            L.append({"name":j.auditor.first_name,"isaudit":j.isaudit,"ispass":j.ispass,"time":j.audit_time.strftime('%Y-%m-%d %H:%M:%S'),"postil":j.postil})
            
        res[i.name] = {"member":L,"date":j.audit_time.strftime('%Y-%m-%d'),"time":j.audit_time.strftime('%H:%M:%S'),"status":status}


    if data.loss_efficacy: return render(request,'gitfabu/my_task_details.html',locals())
    if data.table_name == "git_deploy":
        classify = "fabu"
        try:
            df = eval(data.table_name).objects.get(pk=data.uuid)
        except:
            return render(request,'gitfabu/my_task_details.html',locals())
        dflog = df.deploy_logs.filter(name="发布")
        gitprivate = git_coderepo.objects.filter(platform=df.platform,classify=df.classify,ispublic=False,title=df.name)
        
        auditors = git_deploy_audit.objects.filter(platform=df.platform,classify=df.classify,name="发布")
        if df.platform == "现金网" or df.platform == "蛮牛":
            fabu_details = True
            domains = df.business.domain.filter(classify=df.classify,use=0)
            ag_domains = df.business.domain.filter(classify=df.classify,use=1)
            backend_domains = df.business.domain.filter(classify=df.classify,use=2)
            gitpublic = git_coderepo.objects.filter(platform=df.platform,classify=df.classify,ispublic=True)
            servers = git_ops_configuration.objects.filter(platform=df.platform,classify=df.classify,name="源站")
        else:
            fabu_details = False
            domains = None
            servers = git_ops_configuration.objects.filter(platform=df.platform,classify=df.classify,name=df.name)
    else:
        classify = "gengxin"
        df = eval(data.table_name).objects.get(pk=data.uuid)
        deploy_data = df.code_conf
        if deploy_data: #如果有项目外键
            dflog = deploy_data.deploy_logs.filter(name="更新",update=df.id)
            auditors = git_deploy_audit.objects.filter(platform=deploy_data.platform,classify=deploy_data.classify,name="更新",isurgent=df.isurgent)
            if df.method == "php_pc" or df.method == "php_mobile" or df.method == "js_pc" or df.method == "js_mobile":
                name = "%s-电脑端更新"% df.method
                repo = git_coderepo.objects.get(platform="现金网",classify=deploy_data.classify,title=df.method,ispublic=True).address
            elif df.method == "php" or df.method == "config" or df.method == "js":
                name = "蛮牛%s-公共代码更新"% df.method
                repo = git_coderepo.objects.get(platform="蛮牛",classify=deploy_data.classify,title="mn_"+df.method,ispublic=True).address
            else:
                name = "%s-更新"% deploy_data.name
                repo = git_coderepo.objects.get(platform=deploy_data.platform,classify=deploy_data.classify,ispublic=False,title=deploy_data.name).address
            version = df.version
            branch = df.branch
            version_details = df.details
        else: #没有项目外键，判断属于公共代码全部更新
            dflog = git_deploy_logs.objects.filter(name="更新",update=df.id)
            if "huidu" in df.name: env = "huidu"
            if "online" in df.name: env = "online"
            if "test" in df.name: env= "test"
            if "现金网" in df.name: platform = "现金网"
            if "蛮牛" in df.name: platform = "蛮牛"
            if env == "test":
                auditors = None
            else:
                auditors = git_deploy_audit.objects.filter(platform=platform,classify=env,name="更新",isurgent=df.isurgent)
            if df.method == "php_pc" or df.method == "php_mobile" or df.method == "js_pc" or df.method == "js_mobile":
                repo = git_coderepo.objects.get(platform=platform,classify=env,title=df.method,ispublic=True).address
                name = "%s-电脑端更新"% df.method
            elif df.method == "php" or df.method == "config" or df.method == "js":
                repo = git_coderepo.objects.get(platform=platform,classify=env,title="mn_"+df.method,ispublic=True).address
                name = "蛮牛%s-公共代码更新"% df.method
            version = df.version
            branch = df.branch
            version_details = df.details
    return render(request,'gitfabu/my_task_details.html',locals())


def confirm_mytask(request,uuid):
    """实现get方式复核，将git_deploy的isops为真，mytask的ispass为真"""
    mytask = git_task_audit.objects.get(pk=uuid)
    task = mytask.request_task
    df = eval(task.table_name).objects.get(pk=task.uuid)
    f_domains = df.business.domain.filter(classify=df.classify,use=0) #use=0前端域名，1为ag域名，2为后台域名
    a_domains = df.business.domain.filter(classify=df.classify,use=1)
    b_domains = df.business.domain.filter(classify=df.classify,use=2)
    if request.method == "POST":
        #重置网站状态
        ok = request.POST.get('isok')
        print ok
        if ok=="yes":
            WebSite = eval(task.table_name).objects.filter(pk=task.uuid)
            WebSite.update(isops=True)
            #修改任务状态
            task.isend = True
            task.status = "已完成"
            task.save()
            #修改审核任务状态
            mytask.isaudit = True
            mytask.ispass = True
            mytask.save()
            #重置其他组任务状态
            user = request.user
            groups = task.reqt.filter(auditor=user)
            postil = "复核完成"
            #目前只有工程一个组，如果是多个组，下面还要写判断
            for i in groups:
                check_group_audit(task.id,user.username,True,i.audit_group_id,postil)
            return JsonResponse({'res':"OK"},safe=False)
        else:
            return JsonResponse({'res':"OK"},safe=False)
    return render(request,'gitfabu/confirm_mytask.html',locals())


@login_required
def audit_my_task(request,uuid):
    """审核任务，分发布与更新的审核后续处理"""
    data = git_task_audit.objects.get(pk=uuid)
    df = eval(data.request_task.table_name).objects.get(pk=data.request_task.uuid)
    print "项目id：%s任务id：%s"% (df.id,data.request_task.id)
    if request.method == 'POST':
        # if data.isaudit: return JsonResponse({'res':"OK"},safe=False) #防止重复审核
        ispass = request.POST.get('ispass')
        if ispass == "yes":
            ok = True
        else:
            ok = False
        postil = request.POST.get('postil')
        data.isaudit = True
        data.ispass = ok 
        data.postil = postil
        data.save()

        user = request.user
        print "当前审核人：%s"% user.username
        groups = data.request_task.reqt.filter(auditor=user)
        for i in groups:
            check_group_audit(data.request_task.id,user.username,ok,i.audit_group_id,postil) #检测组成员审核情况的函数
        alldata = data.request_task.reqt.all()

        if False not in [i.isaudit for i in alldata]: #所有人都审核完毕
            if False not in [i.ispass for i in alldata]: #所有人都通过
                print "所有审核已通过，开始更新发布"
                print [i.ispass for i in alldata]
                data.request_task.status="通过审核，更新中"
                data.request_task.save()
                df.isaudit= True
                df.save()
                print "项目id：%s任务id：%s"% (df.id,data.request_task.id)
                if data.request_task.table_name == "git_deploy":
                    reslut = git_fabu_task.delay(df.id,data.request_task.id)
                else:
                    if df.code_conf:
                        reslut = git_update_task.delay(data.request_task.uuid,data.request_task.id)
                    else:
                        if "现金网" in df.name: platform="现金网"
                        if "蛮牛" in df.name: platform="蛮牛"
                        reslut = git_update_public_task.delay(data.request_task.uuid,data.request_task.id,platform=platform)
            else: #有人未通过
                data.request_task.status="未通过审核"
                data.request_task.isend=True
                data.request_task.save()
                df.isaudit= True  #更新任务已审核
                df.islog= True    #更新任务已完成
                if data.request_task.table_name == "git_code_update":
                    if df.code_conf:
                        df.code_conf.islock=False
                        df.code_conf.save()
                    else:
                        if "现金网" in df.name: platform="现金网"
                        if "蛮牛" in df.name: platform="蛮牛"
                        if "huidu" in df.name: classify="huidu"
                        if "online" in df.name: classify="online"
                        git_deploy.objects.filter(platform=platform,classify=classify,islock=True).update(islock=False)
                df.save()
        else:  #还有人未审核
            audit_data = data.request_task.reqt.filter(isaudit=True)
            if False in [i.ispass for i in audit_data]:
                data.request_task.status="未通过审核"
                data.request_task.isend=True
                data.request_task.save()
                df.isaudit= True  #更新任务已审核
                df.islog= True    #更新任务已完成
                if data.request_task.table_name == "git_code_update":
                    if df.code_conf:
                        df.code_conf.islock=False
                        df.code_conf.save()
                    else:
                        if "现金网" in df.name: platform="现金网"
                        if "蛮牛" in df.name: platform="蛮牛"
                        if "huidu" in df.name: classify="huidu"
                        if "online" in df.name: classify="online"
                        git_deploy.objects.filter(platform=platform,classify=classify,islock=True).update(islock=False)
                df.save()
        return JsonResponse({'res':"OK"},safe=False)
    return render(request,'gitfabu/audit_my_task.html',locals())

@login_required
def one_key_task(request,uuid):
    data = git_task_audit.objects.get(pk=uuid)
    df = eval(data.request_task.table_name).objects.get(pk=data.request_task.uuid)
    print "项目id：%s任务id：%s"% (df.id,data.request_task.id)
    if request.method == 'POST':
        if data.isaudit: return JsonResponse({'res':"OK"},safe=False) #防止重复审核
        ispass = request.POST.get('ispass')
        if ispass == "yes":
            ok = True
        else:
            ok = False
        postil = request.POST.get('postil')
        data.isaudit = True
        data.ispass = ok
        data.postil = postil
        data.save()
        onekey_access(data.request_task.id,request.user.username,ok)
        if ok:
            df.isaudit= True
            df.save()
            print "项目id：%s任务id：%s"% (df.id,data.request_task.id)
            if data.request_task.table_name == "git_deploy":
                reslut = git_fabu_task.delay(df.id,data.request_task.id)
            else:
                if df.code_conf:
                    reslut = git_update_task.delay(data.request_task.uuid,data.request_task.id)
                else:
                    if "现金网" in df.name: platform="现金网"
                    if "蛮牛" in df.name: platform="蛮牛"
                    reslut = git_update_public_task.delay(data.request_task.uuid,data.request_task.id,platform=platform)
        else:
            df.isaudit= True
            df.islog= True
            if data.request_task.table_name == "git_code_update":
                if df.code_conf:
                    df.code_conf.islock=False
                    df.code_conf.save()
                else:
                    if "现金网" in df.name: platform="现金网"
                    if "蛮牛" in df.name: platform="蛮牛"
                    if "huidu" in df.name: classify="huidu"
                    if "online" in df.name: classify="online"
                    git_deploy.objects.filter(platform=platform,classify=classify,islock=True).update(islock=False)
            df.save()
        return JsonResponse({'res':"OK"},safe=False)
    return render(request,'gitfabu/one_key_task.html',locals())


@login_required
def web_update_code(request,uuid):
    """一个更新任务添加，现获取所有的分支信息，线上环境只有master分支展示"""
    data = git_deploy.objects.get(pk=uuid)

    WaitTask = data.deploy_update.filter(islog=False)
    if not WaitTask: WaitTask = git_code_update.objects.filter(name__contains=data.platform,islog=False)

    if data.old_reversion:
        old_reversion = data.old_reversion.split('\r\n')[0:5]
    else:
        old_reversion = []

    if request.method == 'GET':
        if data.platform == "现金网" or data.platform == "蛮牛":
            all_branch = ['master']
            web_commits = []
        else:
            all_branch = git_moneyweb_deploy(uuid).deploy_all_branch(what='web')
            web_commits = git_moneyweb_deploy(uuid).branch_checkout(what='web')

    if request.method == 'POST':
        #先判断这个站是否被锁住了，没有锁就继续
        memo = request.POST.get('memo')
        method = request.POST.get('method')
        release = request.POST.get('release')
        branch = request.POST.get('branch')
        #获取当前版本号,组成新版本信息
        old_data = git_code_update.objects.get(code_conf=data,islog=True,isuse=True)
        web_branches = old_data.web_branches
        web_release = old_data.web_release
        php_pc_branches = old_data.php_pc_branches
        php_pc_release = old_data.php_pc_release
        php_mobile_branches = old_data.php_mobile_branches
        php_moblie_release = old_data.php_moblie_release
        js_pc_branches = old_data.js_pc_branches
        js_pc_release = old_data.js_pc_release
        js_mobile_branches = old_data.js_mobile_branches
        js_mobile_release = old_data.js_mobile_release
        config_branches = old_data.config_branches
        config_release = old_data.config_release
        if method == 'web':
            web_release = release[0:7]
            web_branches = branch
        elif method == "php_pc" or method == "php":
            php_pc_release = release[0:7]
            php_pc_branches = branch
        elif method == "php_mobile":
            php_moblie_release = release[0:7]
            php_mobile_branches = branch
        elif method == "js_pc" or method == "js":
            js_pc_release = release[0:7]
            js_pc_branches = branch
        elif method == "js_mobile":
            js_mobile_release = release[0:7]
            js_mobile_branches = branch
        else:
            config_branches = branch
            config_release = release[0:7]
        #判断是否紧急
        if data.platform == "现金网" or data.platform == "蛮牛":
            if data.classify == 'huidu' or data.classify == 'online':
                normal_auditor = git_deploy_audit.objects.get(platform=data.platform,classify=data.classify,isurgent=False,name="更新") #正常审核人
                php_auditor = git_deploy_audit.objects.get(platform=data.platform,classify=data.classify,isurgent=False,name="php更新") #PHP代码正常审核人
                urgent_auditor = git_deploy_audit.objects.get(platform=data.platform,classify=data.classify,isurgent=True,name="更新") #紧急审核人
                c = int(normal_auditor.start_time.replace(":",""))
                d = int(normal_auditor.end_time.replace(":",""))
                now = time.strftime('%H:%M',time.localtime(time.time()))
                e = int(now.replace(":",""))
                if data.classify == 'online':
                    if c <= e and d >= e:
                        print("normal不紧急")
                        if method == "php_pc" or method == "php_mobile" or method == "php" or method == "config":
                            auditor = php_auditor
                        else:
                            auditor = normal_auditor
                        print auditor.name
                        isurgent = False
                        name = data.platform+"-"+data.classify+"-"+data.name+"-"+method+"-更新"
                    else:
                        print("urgent紧急更新")
                        auditor = urgent_auditor
                        isurgent = True
                        name = data.platform+"-"+data.classify+"-"+data.name+"-"+method+"-紧急更新"
                else:
                    if method == "php_pc" or method == "php_mobile" or method == "php" or method == "config":
                        auditor = php_auditor
                    else:
                        auditor = normal_auditor
                    print auditor.name
                    isurgent = False
                    name = data.platform+"-"+data.classify+"-"+data.name+"-"+method+"-更新"
            else:
                isurgent = False
                name = data.platform+"-"+data.classify+"-"+data.name+"-"+method+"-更新"
        else:
            name = data.platform+"-"+data.classify+"-"+data.name+"-更新"
            normal_auditor = git_deploy_audit.objects.get(platform=data.platform,classify=data.classify,isurgent=False,name="更新")
            auditor = normal_auditor
            isurgent = False
        #保存更新版本信息
        updata = git_code_update(name=name,code_conf=data,method=method,version=release[0:7],branch=branch,web_release=web_release,php_pc_release=php_pc_release,
            php_moblie_release=php_moblie_release,js_pc_release=js_pc_release,js_mobile_release=js_mobile_release,config_release=config_release,
            web_branches=web_branches,php_pc_branches=php_pc_branches,php_mobile_branches=php_mobile_branches,js_pc_branches=js_pc_branches,
            js_mobile_branches=js_mobile_branches,config_branches=config_branches,memo=memo,details=release,isurgent=isurgent,last_version=data.now_reversion)
        updata.save()
        #给此项目上锁
        data.islock = True
        data.save()
        #创建更新申请
        mydata = my_request_task(name=name,table_name="git_code_update",uuid=updata.id,memo=memo,initiator=request.user,status="审核中")
        mydata.save()
        #创建审核，测试环境不需要审核
        if data.name == "1029": #现金网1029特例
            mydata.status="通过审核，更新中"
            mydata.save()
            updata.isaudit = True
            updata.save()
            reslut = git_update_task.delay(updata.id,mydata.id)
        else:
            if data.classify == 'huidu' or data.classify == 'online':
                task_distributing(mydata.id,auditor.id)
            else:
                mydata.status="通过审核，更新中"
                mydata.save()
                updata.isaudit = True
                updata.save()
                reslut = git_update_task.delay(updata.id,mydata.id)
        return JsonResponse({'res':"OK"},safe=False)

    return render(request,'gitfabu/web_update_code.html',locals())

def public_update_code(request,env):
    """公共代码更新"""
    if "online" in env:
        classify = "online"
    elif "huidu" in env:
        classify = "huidu"
    elif "test" in env:
        classify = "test"

    if "money" in env:
        base_export_dir = "/data/moneyweb/" + classify + "/export/php_pc"
        platform = "现金网"
    elif "manniu" in env:
        base_export_dir = "/data/manniuweb/" + classify + "/export/mn_php"
        platform = "蛮牛"

    gitrepo = Repo(base_export_dir)
    all_branch = gitrepo.git_all_branch()
    commit = gitrepo.show_commit()
    WaitTask = git_deploy.objects.filter(platform=platform,classify=classify,islock=True) #如果某个站有锁，则无法申请全站更新

    if request.method == 'POST':
        memo = request.POST.get('memo')
        method = request.POST.get('method')
        release = request.POST.get('release')
        branch = request.POST.get('branch')

        #判断是否紧急,huidu没有紧急
        if classify == 'huidu' or classify == 'online':
            normal_auditor = git_deploy_audit.objects.get(platform=platform,classify=classify,isurgent=False,name="更新") #正常审核人
            php_auditor = git_deploy_audit.objects.get(platform=platform,classify=classify,isurgent=False,name="php更新") #PHP代码正常审核人
            urgent_auditor = git_deploy_audit.objects.get(platform=platform,classify=classify,isurgent=True,name="更新") #紧急审核人
            c = int(normal_auditor.start_time.replace(":",""))
            d = int(normal_auditor.end_time.replace(":",""))
            now = time.strftime('%H:%M',time.localtime(time.time()))
            e = int(now.replace(":",""))
            if classify == 'online':
                if c <= e and d >= e:
                    if method == "php_pc" or method == "php_mobile" or method == "php" or method == "config":
                        auditor = php_auditor
                    else:
                        auditor = normal_auditor
                    print auditor.name
                    isurgent = False
                    name = platform +"-"+classify+"-公共代码-"+method+"-更新"
                else:
                    auditor = urgent_auditor
                    isurgent = True
                    name = platform +"-"+classify+"-公共代码-"+method+"-紧急更新"
            else:
                if method == "php_pc" or method == "php_mobile" or method == "php" or method == "config":
                    auditor = php_auditor
                else:
                    auditor = normal_auditor
                print auditor.name
                isurgent = False
                name = platform +"-"+classify+"-公共代码-"+method+"-更新"
        else:
            isurgent = False
            name = platform +"-"+classify+"-公共代码-"+method+"-更新"
        #保存更新任务
        updata = git_code_update(name=name,method=method,version=release[0:7],branch=branch,memo=memo,details=release,isurgent=isurgent)
        updata.save()
        #创建更新申请
        mydata = my_request_task(name=name,table_name="git_code_update",uuid=updata.id,memo=memo,initiator=request.user,status="审核中")
        mydata.save()
        git_deploy.objects.filter(platform=platform,classify=classify,islog=True,usepub=True).update(islock=True) #迁移的时候别忘记把所有的项目usepub项更新为真
        #创建审核
        if classify == "test":
            mydata.status="通过审核，更新中"
            mydata.save()
            updata.isaudit = True
            updata.save()
            reslut = git_update_public_task.delay(updata.id,mydata.id,platform=platform)
        else:
            task_distributing(mydata.id,auditor.id)
        return JsonResponse({'res':"OK"},safe=False)
    return render(request,'gitfabu/public_update_code.html',locals())

def ops_confguration(request):
    """配置页面，包含审核人，线上服务器，公用public地址"""
    repo_data = git_coderepo.objects.filter(platform="现金网",ispublic=True)
    audit_data = git_deploy_audit.objects.filter(platform="现金网")
    ops_data = git_ops_configuration.objects.filter(platform="现金网")
    return render(request,'gitfabu/ops_confguration.html',locals())

def batch_change(request,uuid):
    """切换分支并获取最新的版本号10条"""
    env = request.GET.get('env')
    method = request.GET.get('method')
    branch = request.GET.get('branch')
    if env == "moneyweb":
        print "现金网查询版本号"
        if not method:
            res = {'res':"OK",'branches':[],"commit":[]}
            return JsonResponse(res,safe=False)
        if branch:
            web_commits = git_moneyweb_deploy(uuid).branch_checkout(what=method,branch=branch)
            res = {'res':"OK","commit":web_commits}
        else:
            all_branch = git_moneyweb_deploy(uuid).deploy_all_branch(what=method)
            web_commits = git_moneyweb_deploy(uuid).branch_checkout(what=method)
            res = {'res':"OK",'branches':all_branch,"commit":web_commits}
    else:
        print "蛮牛网查询版本号"
        if not method:
            res = {'res':"OK",'branches':[],"commit":[]}
            return JsonResponse(res,safe=False)
        if branch:
            web_commits = manniu_web_deploy(uuid).branch_checkout(what=method,branch=branch)
            res = {'res':"OK","commit":web_commits}
        else:
            data = manniu_web_deploy(uuid)
            all_branch = data.deploy_all_branch(what=method)
            web_commits = manniu_web_deploy(uuid).branch_checkout(what=method)
            res = {'res':"OK",'branches':all_branch,"commit":web_commits}
    return JsonResponse(res,safe=False)

def public_branch_change(request):
    name = request.GET.get('name')
    env = request.GET.get('env')
    branch = request.GET.get('branch')

    if "online" in env:
        classify = "online"
    elif "huidu" in env:
        classify = "huidu"
    elif "test" in env:
        classify = "test"

    if "money" in env:
        base_dir = "/data/moneyweb/" + classify + "/export/"
        platform = "现金网"
    elif "manniu" in env:
        base_dir = "/data/manniuweb/" + classify + "/export/"
        platform = "蛮牛"


    if name == 'php_pc' or name == 'php_mobile' or name == 'js_pc' or name == 'js_mobile':
        path = base_dir + name
    elif name == 'php' or name == 'js' or name == 'config':
        path = base_dir + "mn_"+name

    gitrepo = Repo(path)
    if branch:
        gitrepo.git_checkout(branch)
        gitrepo.git_pull()
        commit = gitrepo.show_commit()
        res = {'res':"OK","commit":commit}
    else:
        gitrepo.git_checkout('master')
        gitrepo.git_pull()
        all_branch = gitrepo.git_all_branch()
        commit = gitrepo.show_commit()
        res = {'res':"OK",'branches':all_branch,"commit":commit}
    return JsonResponse(res,safe=False)

@login_required
def manniu_list(request):
    data = git_deploy.objects.filter(platform="JAVA项目",classify="online",isops=True,islog=True) #蛮牛java组件项目
    data_huidu = git_deploy.objects.filter(platform="蛮牛",classify="huidu",isops=True,islog=True)
    data_online = git_deploy.objects.filter(platform="蛮牛",classify="online",isops=True,islog=True)
    return render(request,'gitfabu/manniu_list.html',locals())

@login_required
def audit_list(request):
    data = git_deploy_audit.objects.all().order_by('platform','classify')
    return render(request,'gitfabu/audit_list.html',locals())

def audit_manage(request,uuid):
    data = git_deploy_audit.objects.get(pk=uuid)
    uf = git_deploy_audit_from(instance=data)
    all_group = department_Mode.objects.all()
    select_group = data.group.all()
    unselect_group = [i for i in all_group if i not in select_group]

    if request.method == 'POST':
        print request.POST.get('name')
        uf = git_deploy_audit_from(request.POST, instance=data)
        if uf.is_valid():
            member = uf.save(commit=False)
            member.save()
            uf.save_m2m()
            return HttpResponseRedirect('/allow/welcome/')

    return render(request,'gitfabu/audit_manage.html',locals())

def task_observer(request):
    """写一个任务追踪模块，专门用于查看发布任务进度的，但是不能用于审核，只有查看的功能"""
    #fabu_tasks = my_request_task.objects.filter(table_name="git_deploy")
    fabu_tasks = my_request_task.objects.filter(loss_efficacy=False,isend=False)
    #去除重复的审核人

    return render(request,'gitfabu/task_observer.html',locals())
