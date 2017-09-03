#!/usr/bin/env python
# -*- coding:utf-8 -*-
from random import Random

from django.core.mail import send_mail

from mooc.settings import EMAIL_FROM
from users.models import EmailVerifyRecord


def random_str(randomlength=8):
    str = ''
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def send_register_email(email, send_type='register'):
    email_record = EmailVerifyRecord()
    code = random_str(48)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()

    email_title = ''
    email_body = ''

    if send_type == 'register':
        email_title = '慕课在线注册激活链接'
        email_body = '请点击下面的链接激活你的账号：http://127.0.0.1:8000/active{}'.format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            # print('发送成功')
    elif send_type == 'forget':
        email_title = '慕课在线重置密码链接'
        email_body = '请点击下面的链接重置你的账号：http://127.0.0.1:8000/reset/{}'.format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            # print('发送成功')
    elif send_type == 'update_email':
        email_title = '慕课在线邮箱修改验证码'
        email_body = '你的邮箱验证号为：{}'.format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            # print('发送成功')






