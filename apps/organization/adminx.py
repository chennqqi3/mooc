#!/usr/bin/env python
# -*- coding:utf-8 -*-

import xadmin

from .models import CityDict, CourseOrg, Teacher


class CityDictAdmin(object):
    list_display = ['name', 'desc', 'add_time']
    search_fields = ['name', 'desc']
    list_filter = ['name', 'desc', 'add_time']
    readonly_fields = ['add_time']  # 只读字段


class CourseOrgAdmin(object):
    list_display = ['name', 'desc', 'click_nums', 'fav_nums', 'address', 'city', 'add_time']
    search_fields = ['name', 'desc', 'click_nums', 'fav_nums', 'address', 'city']
    list_filter = ['name', 'desc', 'click_nums', 'fav_nums', 'address', 'city', 'add_time']
    readonly_fields = ['add_time', 'click_nums', 'fav_nums']  # 只读字段
    ordering = ['-click_nums']  # 排序规则


class TeacherAdmin(object):
    list_display = ['name', 'org', 'work_years', 'work_company', 'work_position', 'points', 'click_nums', 'fav_nums', 'add_time']
    search_fields = ['name', 'org', 'work_company', 'work_position', 'points']
    list_filter = ['name', 'org', 'work_years', 'work_company', 'work_position', 'points', 'click_nums', 'fav_nums', 'add_time']
    readonly_fields = ['add_time', 'click_nums', 'fav_nums']  # 只读字段
    ordering = ['-click_nums']  # 排序规则

xadmin.site.register(CityDict, CityDictAdmin)
xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(Teacher, TeacherAdmin)


