from datetime import datetime

from django.db import models

from organization.models import CourseOrg, Teacher


class Course(models.Model):
    course_org = models.ForeignKey(CourseOrg, verbose_name='课程机构', null=True, blank=True)
    teacher = models.ForeignKey(Teacher, verbose_name='讲师', null=True, blank=True)
    is_banner = models.BooleanField(default=False, verbose_name='是否轮播')
    name = models.CharField(max_length=50, verbose_name='课程名')
    desc = models.CharField(max_length=400, verbose_name='课程描述')
    detail = models.TextField(verbose_name='课程详情')
    degree = models.CharField(choices=(('cj', '初级'), ('zj', '中级'), ('gj', '高级')), verbose_name='课程难度', max_length=5)
    learn_time = models.IntegerField(default=0, verbose_name='学习时长(分钟数)')
    students = models.IntegerField(default=0, verbose_name='学习人数')
    fav_nums = models.IntegerField(default=0, verbose_name='收藏人数')
    image = models.ImageField(upload_to='courses/%Y/%m', verbose_name='课程封面图', max_length=100)
    click_nums = models.IntegerField(default=0, verbose_name='点击数')
    category = models.CharField(default='后端开发', max_length=20, verbose_name='课程类别')
    tag = models.CharField(default='', max_length=10, verbose_name='课程标签')
    youneed_know = models.CharField(default='', max_length=400, verbose_name='课程须知')
    teacher_tell = models.CharField(default='', max_length=400, verbose_name='老师告诉你')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = verbose_name

    def get_lesson_num(self):
        # 获取章节数
        return self.lesson_set.all().count()

    get_lesson_num.short_description = '章节数'

    def get_learn_users(self):
        return self.usercourse_set.all()[:5]

    def get_course_lesson(self):
        # 返回课程章节
        return self.lesson_set.all()

    def get_course_resource(self):
        # 返回课程资源
        return self.courseresource_set.all()

    def __str__(self):
        return self.name


class BannerCourse(Course):
    class Meta:
        verbose_name = '轮播课程'
        verbose_name_plural = verbose_name
        proxy = True


class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name='课程')
    name = models.CharField(max_length=100, verbose_name='章节名')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '章节'
        verbose_name_plural = verbose_name

    def get_lesson_video(self):
        return self.video_set.all()

    def __str__(self):
        return '{}({})'.format(self.course.name, self.name)


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name='课程')
    name = models.CharField(max_length=100, verbose_name='视频名')
    url = models.CharField(max_length=200, default='', verbose_name='访问地址')
    learn_time = models.IntegerField(default=0, verbose_name='学习时长(分钟数)')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '视频'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseResource(models.Model):
    course = models.ForeignKey(Course, verbose_name='课程')
    name = models.CharField(max_length=100, verbose_name='课程资源名')
    download = models.FileField(upload_to='course/resource/%Y/%m', verbose_name='资源文件', max_length=100)
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '课程资源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name



