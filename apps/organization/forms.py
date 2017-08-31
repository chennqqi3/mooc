#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
from django import forms

from operation.models import UserAsk


class UserAskForm(forms.ModelForm):
    class Meta:
        model = UserAsk
        fields = ['name', 'mobile', 'course_name']

    def clean_mobile(self):
        mobile = self.cleaned_data['mobile']
        p = re.compile(r'^\d{11}$')
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError('手机号码不正确', code='mobile_invalid')







