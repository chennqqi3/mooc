from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, PageNotAnInteger

from courses.models import Course, CourseResource, Video

from operation.models import UserFavorite, UserComments, UserCourse


# 判断是否收藏函数#########
from utils.mixin_utils import LoginRequiredMixin


def has_fav(request, id, fav_type):
    if request.user.is_authenticated():
        if UserFavorite.objects.filter(user=request.user, fav_id=id, fav_type=fav_type):
            return True
    return False

##########################


class CourseList(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by('-add_time')
        hot_courses = Course.objects.all().order_by('-click_nums')[:3]

        # 搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_courses = all_courses.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords) | Q(detail__icontains=search_keywords))

        # 课程排序
        sort = request.GET.get('sort', '')
        if sort == 'students':
            all_courses = all_courses.order_by('-students')
        elif sort == 'hot':
            all_courses = all_courses.order_by('-click_nums')

        # 对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_courses, 6, request=request)
        courses = p.page(page)

        return render(request, 'course-list.html', {
            'all_courses': courses,
            'sort': sort,
            'hot_courses': hot_courses,
        })


class CourseDetailView(View):
    """
    课程详情页逻辑
    """
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()

        if course.tag:
            relate_courses = Course.objects.filter(tag=course.tag)[:1]
        else:
            relate_courses = []

        return render(request, 'course-detail.html', {
            'course': course,
            'relate_courses': relate_courses,
            'has_fav_course': has_fav(request, course.id, 1),
            'has_fav_org': has_fav(request, course.course_org.id, 2),
        })


class CourseInfoView(LoginRequiredMixin, View):
    """
    课程章节信息
    """

    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        course.students += 1
        course.save()

        # 查询用户是否已经关联该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        # 不存在关联则添加这个关联
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        user_courses = UserCourse.objects.filter(course=course)  # 查询用户课程
        user_ids = [user_course.user.id for user_course in user_courses]  # 找出所有学过该课程的用户id
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [user_course.course.id for user_course in all_user_courses]  # 找出所有学过该课程的所有用户所学的所有课程的id
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]
        return render(request, 'course-video.html', {
            'course': course,
            'relate_courses': relate_courses,
        })


class CourseCommentView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        all_comments = UserComments.objects.all().order_by('-add_time')
        return render(request, 'course-comment.html', {
            'course': course,
            'all_comments': all_comments,
        })


class AddCommentView(View):
    """
    用户添加评论
    """
    def post(self, request):
        # 判断用户登录状态
        if not request.user.is_authenticated():
            return HttpResponse('{"status": "fail", "msg": "用户未登录"}', content_type='application/json')

        course_id = request.POST.get('course_id', '')
        comments = request.POST.get('comments', '')
        if int(course_id)> 0 and comments:
            course_comments = UserComments()
            course = Course.objects.get(id=int(course_id))
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse('{"status": "success", "msg": "添加成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status": "fail", "msg": "添加失败"}', content_type='application/json')


class VideoPlayView(View):
    """
    视频播放页面
    """
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course

        # 查询用户是否已经关联该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        # 不存在关联则添加这个关联
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        user_courses = UserCourse.objects.filter(course=course)  # 查询用户课程
        user_ids = [user_course.user.id for user_course in user_courses]  # 找出所有学过该课程的用户id
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [user_course.course.id for user_course in all_user_courses]  # 找出所有学过该课程的所有用户所学的所有课程的id
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]
        return render(request, 'course-play.html', {
            'course': course,
            'relate_courses': relate_courses,
            'video': video,
        })




