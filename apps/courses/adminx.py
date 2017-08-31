#!/usr/bin/env python
# -*- coding:utf-8 -*-
import xadmin

from .models import Course, CourseResource, Lesson, Video, BannerCourse


class LessonInline(object):
    model = Lesson
    extra = 0


class CourseResourceInline(object):
    model = CourseResource
    extra = 0


class CourseAdmin(object):
    # 显示字段
    list_display = ['name', 'desc', 'degree', 'learn_time', 'students', 'fav_nums', 'is_banner', 'click_nums', 'get_lesson_num', 'add_time']
    search_fields = ['name', 'degree', 'learn_time', 'students', 'fav_nums', 'click_nums']  # 可搜索字段
    list_filter = ['name', 'degree', 'learn_time', 'students', 'fav_nums', 'click_nums', 'add_time']  # 可过滤字段
    list_editable = ['name', 'degree', 'is_banner']  # 列表页可编辑字段
    ordering = ['-click_nums']  # 排序规则
    readonly_fields = ['fav_nums', 'click_nums', 'add_time']  # 只读字段
    inlines = [LessonInline, CourseResourceInline]  # 外键内嵌
    refresh_times = [10, 50, 100]

    def save_models(self):
        """
        保存修改时自动调用的逻辑,新增课程时，自动修改对应课程机构的课程数量
        :return:
        """
        obj = self.new_obj
        obj.save()
        if obj.course_org is not None:
            course_org = obj.course_org
            course_org.course_nums = Course.objects.filter(course_org=course_org).count()
            course_org.save()

    def queryset(self):
        """
        获取字段时自动调用方法，显示非轮播图
        :return:
        """
        qs = super(CourseAdmin, self).queryset()
        qs = qs.filter(is_banner=False)
        return qs


class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'degree', 'learn_time', 'students', 'fav_nums', 'is_banner', 'click_nums', 'add_time']
    search_fields = ['name', 'degree', 'learn_time', 'students', 'fav_nums', 'click_nums']
    list_filter = ['name', 'degree', 'learn_time', 'students', 'fav_nums', 'click_nums', 'add_time']
    ordering = ['-click_nums']
    readonly_fields = ['fav_nums', 'click_nums', 'add_time']
    inlines = [LessonInline, CourseResourceInline]

    def queryset(self):
        """
        显示轮播图
        :return:
        """
        qs = super(BannerCourseAdmin, self).queryset()
        qs = qs.filter(is_banner=True)
        return qs


class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    list_filter = ['course__name', 'name', 'add_time']
    readonly_fields = ['add_time']  # 只读字段


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time']
    readonly_fields = ['add_time']  # 只读字段


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course', 'name']
    list_filter = ['course', 'name', 'add_time']
    readonly_fields = ['add_time']  # 只读字段


xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)

