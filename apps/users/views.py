import json
from datetime import datetime, timedelta

from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.urls import reverse
from django.views.generic.base import View
from pure_pagination import Paginator, PageNotAnInteger


from courses.models import Course
from operation.models import UserCourse, UserFavorite, UserMessage
from organization.models import CourseOrg, Teacher
from users.forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from users.models import UserProfile, EmailVerifyRecord, Banner
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))


class LoginView(View):
    """
    登录页面逻辑
    """
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return render(request, 'login.html', {'msg': '用户未激活!'})
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误!'})
        else:
            return render(request, 'login.html', {'login_form': login_form})


class RegisterView(View):
    """用户注册页面逻辑"""
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            email = request.POST.get('email', '')
            if UserProfile.objects.filter(email=email):
                # 用户查重
                return render(request, 'register.html', {'msg': '用户已存在！', 'register_form': register_form})
            password = request.POST.get('password', '')
            user_profile = UserProfile()
            user_profile.username = email
            user_profile.email = email
            user_profile.password = make_password(password)
            user_profile.is_active = False  # 初始设置为未激活状态
            user_profile.save()

            # 欢迎注册消息
            user_message = UserMessage()
            user_message.user = user_profile.id  # 是id不是obj
            user_message.message = '欢迎注册慕课在线网'
            user_message.save()


            send_register_email(email, 'register')

            return render(request, 'login.html')

        else:
            return render(request, 'register.html', {'register_form': register_form})


class ActiveUserView(View):
    """用户激活链接页面逻辑"""
    def get(self, request, active_code):
        # all_record = EmailVerifyRecord.objects.filter(code=active_code)
        # if all_record:
        #     for record in all_record:
        #         email = record.email
        #         user = UserProfile.objects.get(email=email)
        #         user.is_active = True
        #         user.save()
        #     return render(request, 'login.html')
        # else:
        #     return render(request, 'active_fail.html')
        try:
            record = EmailVerifyRecord.objects.get(code=active_code)
        except:
            # 不存在这个record就说明失效或是错误链接
            return render(request, 'active_fail.html')

        email = record.email
        user = UserProfile.objects.get(email=email)

        if record.send_time + timedelta(days=3) < datetime.now():
            # 超期就删除这个用户
            email = record.email
            user = UserProfile.objects.get(email=email)
            user.delete()
            return render(request, 'active_fail.html')
        else:
            # 没有超期就激活用户
            user.is_active = True
            user.save()
            return render(request, 'login.html')


class ForgetPwdView(View):
    """
    密码找回页面逻辑
    """
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, 'forgetpwd.html', {'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email', '')
            send_register_email(email, 'forget')
            return render(request, 'send_success.html')
        else:
            # 表单填写不合法
            return render(request, 'forgetpwd.html', {'forget_form': forget_form})


class ResetView(View):
    """
    校验重置密码的链接
    """
    def get(self, request, active_code):

        try:
            record = EmailVerifyRecord.objects.get(code=active_code)
        except:
            # 没有这个记录就说明链接失效
            return render(request, 'active_fail.html')

        if record.send_time + timedelta(days=3) < datetime.now():
            # 超出三天的修改时限就删除，并返回失效页面
            record.delete()
            return render(request, 'active_fail.html')
        else:
            email = record.email
            user = UserProfile.objects.get(email=email)
            user.is_active = True  # 将用户激活
            user.save()
            record.delete()  # 成功校验链接， 删除链接防止反复调用
            return render(request, 'password_reset.html', {'email': email})


class ModifyPwd(View):
    """修改密码页面的逻辑"""
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            email = request.POST.get('email', '')
            if pwd1 != pwd2:
                # 校验失败
                return render(request, 'password_reset.html', {'email': email, 'msg': '密码不一致~'})
            else:
                user = UserProfile.objects.get(email=email)
                user.password = make_password(pwd1)
                user.save()
                return render(request, 'login.html')
        else:
            # 表单不合法
            email = request.POST.get('email', '')
            return render(request, 'password_reset.html', {'email': email, 'modify_form': modify_form})

# ############用户中心############ #


class UserInfoView(LoginRequiredMixin, View):
    """
    用户个人信息
    """
    def get(self, request):
        return render(request, 'usercenter-info.html', {})

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')


class UploadImageView(LoginRequiredMixin, View):
    """
    用户修改头像
    """
    def post(self, request):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse('{"status": "fail"}', content_type='application/json')


class UpdatePwdView(View):
    """个人中心修改密码页面的逻辑"""
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                # 校验失败
                return HttpResponse('{"status": "fail", "msg": "密码不一致"}', content_type='application/json')

            else:
                user = request.user
                user.password = make_password(pwd1)
                user.save()
                return HttpResponse('{"status": "success"}', content_type='application/json')

        else:
            # 表单不合法
            email = request.POST.get('email', '')
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


class SendEmailCodeView(LoginRequiredMixin, View):
    """
    发送邮箱验证码
    """
    def get(self, request):
        email = request.GET.get('email', '')
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email": "邮箱已经存在"}', content_type='application/json')

        send_register_email(email, 'update_email')
        return HttpResponse('{"status": "success"}', content_type='application/json')


class UpdateEmailView(LoginRequiredMixin, View):
    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')

        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse('{"email": "验证码错误"}', content_type='application/json')


class MyCourseView(LoginRequiredMixin, View):
    """
    我的课程
    """
    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, 'usercenter-mycourse.html', {
            'user_courses': user_courses,
        })


class MyFavOrgView(LoginRequiredMixin, View):
    """
    我收藏的课程机构
    """
    def get(self, request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, 'usercenter-fav-org.html', {
            'org_list': org_list,
        })


class MyFavTeacherView(LoginRequiredMixin, View):
    """
    我收藏的课程讲师
    """
    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, 'usercenter-fav-teacher.html', {
            'teacher_list': teacher_list,
        })


class MyFavCourseView(LoginRequiredMixin, View):
    """
    我收藏的课程
    """
    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            teacher = Course.objects.get(id=course_id)
            course_list.append(teacher)
        return render(request, 'usercenter-fav-course.html', {
            'course_list': course_list,
        })


class MyMessageView(View):
    """
    我的消息页面逻辑
    """
    def get(self, request):
        all_messages = UserMessage.objects.filter(user=request.user.id)
        all_unread_messages = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()

        # 对个人消息
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_messages, 5, request=request)
        messages = p.page(page)

        return render(request, 'usercenter-message.html', {
            'messages': messages,
        })


class IndexView(View):
    """
    首页逻辑
    """
    def get(self, request):
        # 取出轮播图
        all_banners = Banner.objects.all().order_by('index')
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html', {
            'all_banners': all_banners,
            'courses': courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs,
        })


def page_not_found(request):
    """
    全局404处理
    """
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def page_error(request):
    """
    全局500处理
    """
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response

