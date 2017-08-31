#!/usr/bin/env python
# -*- coding:utf-8 -*-

import xadmin

from .models import EmailVerifyRecord, Banner
from xadmin import views


# #################### Xadmin配置 ####################### #
class BaseSetting(object):

    enable_themes = True  # xadmin是否使用主题
    use_bootswatch = True  # xadmin是否获取主题


class GlobalSetting(object):
    site_title = '慕课网后台管理系统'    # xadmin标题
    site_footer = '慕课网'              # xadmin页脚
    # menu_style = 'accordion'         # xadmin左侧目录样式
# ######################################################## #


class EmailVerifyRecordAdmin(object):
    list_display = ['code', 'email', 'send_type', 'send_time']
    search_fields = ['code', 'email', 'send_type']
    list_filter = ['code', 'email', 'send_type', 'send_time']


class BannerAdmin(object):
    list_display = ['title', 'image', 'url', 'index', 'add_time']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index', 'add_time']


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)

xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSetting)
