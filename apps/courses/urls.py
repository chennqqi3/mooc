#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.conf.urls import url

from courses.views import CourseList, CourseDetailView, CourseInfoView, CourseCommentView, AddCommentView, VideoPlayView

urlpatterns = [
    # 课程列表页
    url(r'^list/$', CourseList.as_view(), name='course_list'),
    url(r'^detail/(?P<course_id>\d+)/$', CourseDetailView.as_view(), name='course_detail'),
    url(r'^info/(?P<course_id>\d+)/$', CourseInfoView.as_view(), name='course_info'),
    # 课程评论
    url(r'^comment/(?P<course_id>\d+)/$', CourseCommentView.as_view(), name='course_comment'),
    # 添加课程评论
    url(r'^add_comment/$', AddCommentView.as_view(), name='add_comment'),
    # 视频
    url(r'^video/(?P<video_id>\d+)/$', VideoPlayView.as_view(), name='video_play'),

]

