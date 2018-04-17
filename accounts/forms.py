#!/usr/bin/python
#-*-coding:utf-8-*-

from django import forms
from .fields import UsernameField,PasswordField
from django.contrib.auth import authenticate,login
from accounts.models import CustomUser, department_Mode,department_auth_cmdb
# from cmdb_auth.models import AuthNode
# from assets.models import project_swan, Host

class UserCreateForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name','last_name', 'email', 'mobile', "user_key")

class useredit_from(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ["first_name", "email", "mobile", "user_key"]

class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        label=u"用户名",
        error_messages={'required': u'请输入用户名'},
        widget=forms.TextInput(
            attrs={
                'placeholder':u"用户名",
            }
        ),
    )
    password = forms.CharField(
        required=True,
        label=u"密码",
        error_messages={'required': u'请输入密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':u"密码",
            }
        ),
    )
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"用户名和密码为必填项")
        else:
            cleaned_data = super(LoginForm, self).clean()

class ChangePasswordForm(forms.Form):
    """
        A form used to change the password of a user in the admin interface.
    """
    newpassword = PasswordField(required=True, max_length=12, min_length=6)
    renewpassword = PasswordField(required=True, max_length=12, min_length=6)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        newpassword = self.cleaned_data.get('newpassword')
        renewpassword = self.cleaned_data.get('renewpassword')
        if newpassword and renewpassword:
            if newpassword != renewpassword:
                raise forms.ValidationError(u"此处必须输入和上栏密码相同的内容")
        return renewpassword

    def save(self, commit=True):
        """
        Saves the new password.
        """
        # print self.user.set_password(self.cleaned_data["newpassword"])
        if commit:
            self.user.save()
        return self.user

class NewPasswordForm(forms.ModelForm):
    newpassword = PasswordField(required=True, max_length=128, min_length=6, label=u'新密码')
    renewpassword = PasswordField(required=True, max_length=128, min_length=6, label=u'确认密码')

    class Meta:
        model = CustomUser
        fields = ['newpassword', 'renewpassword']

class ResetPasswordForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['email']

class department_from(forms.ModelForm):
    class Meta:
        model = department_Mode
        fields = ["name","manager","members"]

class department_auth_addForm(forms.ModelForm):
    u"""给组赋予权限的表单"""

    class Meta:
        model = department_auth_cmdb

        fields = ["show_a_group","add_a_group","edit_a_group","delete_a_group","select_host","update_host","add_host","delete_host","show_pro","add_pro",
        "money_fabu" ,"money_gengxin" ,"manniu_fabu","manniu_gengxin","auth_project","auditor_manage","one_key","add_user","edit_user","edit_pass","delete_user",
        "show_department","add_department","edit_department","delete_department","show_white","edit_white","show_domain","department_name",
        "edit_domain","add_domain","delete_domain","show_nginx","edit_nginx","add_nginx","delete_nginx","show_dns","show_wiki","add_wiki","test_fun","observer"
        ]