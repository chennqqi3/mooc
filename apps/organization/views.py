import json

from django.db.models import Q
from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, PageNotAnInteger
from django.http import HttpResponse

from courses.models import Course
from operation.models import UserFavorite
from .models import CourseOrg, CityDict, Teacher
from .forms import UserAskForm


class OrgView(View):
    """课程机构列表"""
    def get(self, request):
        all_orgs = CourseOrg.objects.all()
        all_citys = CityDict.objects.all()
        # 热门机构
        hot_orgs = CourseOrg.objects.order_by('-click_nums')[:3]

        # 搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))

        # 如果返回了city参数，城市筛选
        city_id = request.GET.get('city', '')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        # 如果返回了ct参数，类别筛选
        category = request.GET.get('ct', '')
        if category:
            all_orgs = all_orgs.filter(category=category)

        # 如果返回了了sort参数，排序筛选
        sort = request.GET.get('sort', '')
        if sort == 'students':
            all_orgs = all_orgs.order_by('-students')
        elif sort == 'courses':
            all_orgs = all_orgs.order_by('-course_nums')

        # 统计最后经过筛选的机构数量
        org_nums = all_orgs.count()


        # 课程机构分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_orgs, 5, request=request)
        orgs = p.page(page)

        return render(request, 'org-list.html', {
            'all_orgs': orgs,
            'all_citys': all_citys,
            'org_nums': org_nums,
            'city_id': city_id,
            'category': category,
            'hot_orgs': hot_orgs,
            'sort': sort,
        })


class AddUserAskView(View):
    """用户咨询表单"""
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            userask_form.save(commit=True)
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            print(userask_form.errors)
            d = {"status": "fail", "msg": "{}".format(userask_form.errors)}
            return HttpResponse(json.dumps(d), content_type='application/json')

# 判断是否收藏函数#########


def has_fav(request, id, fav_type):
    if request.user.is_authenticated():
        if UserFavorite.objects.filter(user=request.user, fav_id=id, fav_type=fav_type):
            return True
    return False

##########################


class OrgHomeView(View):
    """
    机构首页逻辑
    """
    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()
        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:1]

        return render(request, 'org-detail-homepage.html', {
            'all_courses': all_courses,
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': 'home',
            'has_fav': has_fav(request, course_org.id, 2),
        })


class OrgCourseView(View):
    """
    课程机构列表页
    """
    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_courses = course_org.course_set.all()
        return render(request, 'org-detail-course.html', {
            'all_courses': all_courses,
            'course_org': course_org,
            'current_page': 'course',
            'has_fav': has_fav(request, course_org.id, 2),
        })


class OrgDescView(View):
    """
    课程机构介绍页
    """
    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        return render(request, 'org-detail-desc.html', {
            'course_org': course_org,
            'current_page': 'desc',
            'has_fav': has_fav(request, course_org.id, 2),
        })


class OrgTeacherView(View):
    """
    课程机构教师页
    """

    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_teachers = course_org.teacher_set.all()
        return render(request, 'org-detail-teachers.html', {
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': 'teacher',
            'has_fav': has_fav(request, course_org.id, 2),
        })


class AddFavView(View):
    """
    用户收藏与取消收藏
    """
    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)
        fav_type = request.POST.get('fav_type', 0)

        # 判断用户登录状态
        if not request.user.is_authenticated():
            return HttpResponse('{"status": "fail", "msg": "用户未登录"}', content_type='application/json')

        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        if exist_records:
            # 如果记录已经存在， 则表示用户取消收藏
            exist_records.delete()
            if int(fav_type) == 1:
                course = Course.objects.get(id=fav_id)
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif fav_type == 2:
                org = CourseOrg.objects.get(id=fav_id)
                org.fav_nums -= 1
                if org.fav_nums < 0:
                    org.fav_nums = 0
                org.save()
            elif fav_type == 3:
                teacher = Teacher.objects.get(id=fav_id)
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.fav_nums -= 1
            return HttpResponse('{"status": "success", "msg": "收藏"}', content_type='application/json')

        else:
            user_fav = UserFavorite()
            fav_id = int(fav_id)
            fav_type = int(fav_type)
            if fav_id > 0 and fav_type > 0:
                if int(fav_type) == 1:
                    course = Course.objects.get(id=fav_id)
                    course.fav_nums += 1
                    course.save()
                elif fav_type == 2:
                    org = CourseOrg.objects.get(id=fav_id)
                    org.fav_nums += 1
                    org.save()
                elif fav_type == 3:
                    teacher = Teacher.objects.get(id=fav_id)
                    teacher.fav_nums += 1
                user_fav.user = request.user
                user_fav.fav_id = fav_id
                user_fav.fav_type = fav_type
                user_fav.save()

                return HttpResponse('{"status": "success", "msg": "已收藏!"}', content_type='application/json')
            else:
                return HttpResponse('{"status": "fail", "msg": "收藏出错"}', content_type='application/json')

# ############## 讲师相关 ############### #


class TeacherListView(View):
    """
    课程讲师列表页
    """

    def get(self, request):
        all_teachers = Teacher.objects.all()

        hot_teachers = all_teachers.order_by('-click_nums')[:3]

        # 搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_teachers = all_teachers.filter(Q(name__icontains=search_keywords) | Q(work_company__icontains=search_keywords) | Q(work_position__icontains=search_keywords))

        # 如果返回了了sort参数，排序筛选
        sort = request.GET.get('sort', '')
        if sort == 'hot':
            all_teachers = all_teachers.order_by('-click_nums')

        # 讲师列表进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_teachers, 3, request=request)
        teachers = p.page(page)

        return render(request, 'teachers-list.html', {
            'all_teachers': teachers,
            'hot_teachers': hot_teachers,
            'sort': sort,
        })


class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        all_courses = Course.objects.filter(teacher=teacher)
        hot_teachers = Teacher.objects.all().order_by('-click_nums')[:3]

        return render(request, 'teacher-detail.html', {
            'teacher': teacher,
            'all_courses': all_courses,
            'hot_teachers': hot_teachers,
            'has_teacher_fav': has_fav(request, teacher.id, 3),
            'has_org_fav': has_fav(request, teacher.org.id, 2),
        })
