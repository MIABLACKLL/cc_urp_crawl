from cc_course_app.models import WxUser, CcUser, CcExam, CcFile, CcHomework , UrpUser, CcTakes, UrpGrade
from django.http import JsonResponse, HttpResponse
from requests_html import HTMLSession
import urp_crawl
import cc_crawl
import json
import urllib
from django.views.decorators.csrf import csrf_exempt
'''
def getOpenid(code):
    appid = 'wxf718d32463f71447'
    secret = '68512e327676836a1bf0e0135db9b7a7'
    url = "https://api.weixin.qq.com/sns/jscode2session?appid=" + appid + \
          "&secret=" + secret + "&js_code=" + code + "&grant_type=authorization_code"
    result = requests.get(url)
    openid = (result.json())['openid']
    return openid
'''

@csrf_exempt
def login(request):
    if request.method == 'POST':
        # params = request.data
        uuid = (json.loads(request.body))['openid']
        try:
            user = WxUser.objects.get(uuid=uuid)
        except WxUser.DoesNotExist:
            user = WxUser.objects.create(uuid=uuid)
        session = HTMLSession()
        user_id = user.user_id
        ret = {'code': '00000', 'msg': '授权成功', 'data': {'openid': uuid}}
        try:
            cc_id = CcUser.objects.get(user_id=user_id).cc_id
        except CcUser.DoesNotExist:
            cc_id = ''
        try:
            urp_user = UrpUser.objects.get(user_id=user_id).urp_user
        except UrpUser.DoesNotExist:
            urp_user = ''
        return HttpResponse(json.dumps(ret, ensure_ascii=False)
                            , content_type="application/json.charset=utf-8")
    else:
        return HttpResponse(json.dumps({'result': False}, ensure_ascii=False)
                            , content_type="application/json.charset=utf-8")

@csrf_exempt
def boundCc(request):
    if request.method == 'POST':
        post_dict = (json.loads(request.body))
        try:
            user_id = WxUser.objects.get(uuid=post_dict['open_id']).user_id
        except WxUser.DoesNotExist:
            user_id = ''
        cc_username = post_dict['user_id']
        cc_password = post_dict['pass_wd']
        login_form = {'IDToken0': '', 'IDToken1': cc_username, 'IDToken2':cc_password , 'IDButton': 'Login',
                      'goto': 'aHR0cDovL2NjLnNjdS5lZHUuY24vRzJTL1Nob3dzeXN0ZW0vZG9jaGVja2NhLmFzcHg=', 'encoded': 'true',
                      'gx_charset': 'UTF-8'}
        session = HTMLSession()
        session.post(url='http://ids.scu.edu.cn/amserver/UI/Login', data=login_form)
        state_code = session.get(url='http://cc.scu.edu.cn/G2S/MySpace/IndexStudent.aspx',allow_redirects=False).status_code

        if state_code > 300:
            return HttpResponse(json.dumps({'result': False},ensure_ascii=False)
                         , content_type="application/json.charset=utf-8")
        else:
            try:
                CcUser.objects.get(user_id=user_id)
                CcUser.objects.filter(user_id=user_id).update(cc_id=cc_username, cc_password=cc_password,
                                                                user_id=user_id)
            except CcUser.DoesNotExist:
                CcUser.objects.create(cc_id=cc_username,cc_password=cc_password,user_id=user_id)
                cc_crawl.runCrawl(cc_username, cc_password)
            return HttpResponse(json.dumps({'result': True}, ensure_ascii=False)
                         , content_type="application/json.charset=utf-8")
    else:
        return HttpResponse(json.dumps({'result': False}, ensure_ascii=False)
                     , content_type="application/json.charset=utf-8")

@csrf_exempt
def boundUrp(request):
    if request.method == 'POST':
        post_dict = (json.loads(request.body))
        # print(post_dict)
        try:
            user_id = WxUser.objects.get(uuid=post_dict['open_id']).user_id
        except WxUser.DoesNotExist:
            user_id = ''
        urp_username = post_dict['user_id']
        urp_password = post_dict['pass_wd']
        # urp_username = request.POST.get('username', '')
        # urp_password = request.POST.get('password', '')
        try:
            UrpUser.objects.get(user_id=user_id)
            UrpUser.objects.filter(user_id=user_id).delete()
        except UrpUser.DoesNotExist:
            pass
        if urp_crawl.login(urp_username, urp_password, True):
            UrpUser.objects.create(urp_user=urp_username, urp_password=urp_password, user_id=user_id)
            return HttpResponse(json.dumps({'result': True}, ensure_ascii=False)
                                , content_type="application/json.charset=utf-8")
        else:
            return HttpResponse(json.dumps({'result': False}, ensure_ascii=False)
                                , content_type="application/json.charset=utf-8")
    else:
        return HttpResponse(json.dumps({'result': False}, ensure_ascii=False)
                            , content_type="application/json.charset=utf-8")

@csrf_exempt
def getHomework(request):
    if request.method == 'POST':
        post_dict = (json.loads(request.body))
        try:
            user_id = WxUser.objects.get(uuid=post_dict['open_id']).user_id
            cc_id = CcUser.objects.get(user_id=user_id).cc_id
        except CcUser.DoesNotExist:
            cc_id = ''
        #user_id = post_dict['open_id']
        course_queryset = CcTakes.objects.filter(cc_id=cc_id)
        result_dict = {}
        result_list = []
        idnum = 1
        for course in course_queryset:
            homework_queryset = CcHomework.objects.filter(cc_id=cc_id, course_name=course.course_name)
            homework_list = []
            for homework in homework_queryset:
                homework_msg_dict = {}
                if homework.state == "已提交":
                    homework_msg_dict['state'] = False
                else:
                    homework_msg_dict['state'] = True
                homework_msg_dict['id'] = idnum
                homework_msg_dict['course_name'] = homework.course_name
                homework_msg_dict['name'] = homework.name
                homework_msg_dict['end_time'] = homework.end_time
                homework_list.append(homework_msg_dict)
            if homework_list:
                result_list.append(homework_list)
                idnum += 1
        result_dict['data'] = result_list
        return HttpResponse(json.dumps(result_dict, ensure_ascii=False)
                            , content_type="application/json.charset=utf-8")
    if request.method == 'GET':
        return HttpResponse(json.dumps("Only can be posted!", ensure_ascii=False),
                            content_type="application/json.charset=utf-8")

@csrf_exempt
def getExam(request):
    if request.method == 'POST':
        post_dict = (json.loads(request.body))
        try:
            user_id = WxUser.objects.get(uuid=post_dict['open_id']).user_id
            cc_id = CcUser.objects.get(user_id=user_id).cc_id
        except :
            cc_id = ''
        result_dict = {}
        result_list = []
        exam_queryset = CcExam.objects.filter(cc_id=cc_id)
        for exam in exam_queryset:
            exam_dict = {}
            if exam.state == "已提交":
                exam_dict['state'] = False
            else:
                exam_dict['state'] = True
            exam_dict['course_name'] = exam.course_name
            exam_dict['name'] = exam.name
            exam_dict['begin_time'] = exam.begin_time
            exam_dict['end_time'] = exam.end_time
            result_list.append(exam_dict)
        result_dict['data'] = result_list
        return HttpResponse(json.dumps(result_dict, ensure_ascii=False)
                            , content_type="application/json.charset=utf-8")
    if request.method == 'GET':
        return HttpResponse(json.dumps("Only can be posted!", ensure_ascii=False),
                            content_type="application/json.charset=utf-8")
'''
def getAllExam(request):
    if request.method == 'POST':
        result_dict = {}
        result_list = []
        exam_queryset = CcExam.objects.filter(cc_id=cc_id)
        for exam in exam_queryset:
            exam_dict = {}
            exam_dict['course_name'] = exam.course_name
            exam_dict['name'] = exam.name
            exam_dict['begin_time'] = exam.begin_time
            exam_dict['end_time'] = exam.end_time
            result_list.append(exam_dict)
        result_dict['data'] = result_list
        return HttpResponse(json.dumps(result_dict, ensure_ascii=False)
                            , content_type="application/json.charset=utf-8")
    if request.method == 'GET':
        return HttpResponse(json.dumps("Only can be posted!", ensure_ascii=False),
                            content_type="application/json.charset=utf-8")
'''
@csrf_exempt
def getFileName(request):
    if request.method == 'POST':
        post_dict = (json.loads(request.body))
        # print(post_dict)
        teacher_name = post_dict['teacher_name']
        course_name = post_dict['course_name']
        result_dict = {}
        result_list = []
        file_queryset = CcFile.objects.filter(teacher_name=teacher_name, course_name=course_name)
        for file in file_queryset:
            file_dict = {}
            file_dict['course_name'] = course_name
            file_dict['name'] = file.file_name
            result_list.append(file_dict)
        result_dict['data'] = result_list
        return HttpResponse(json.dumps(result_dict, ensure_ascii=False)
                            , content_type="application/json.charset=utf-8")
    if request.method == 'GET':
        return HttpResponse(json.dumps("Only can be posted!", ensure_ascii=False),
                            content_type="application/json.charset=utf-8")

@csrf_exempt
def dowmloadFile(request):
    if request.method == 'GET':
        teacher_name = request.GET['teacher_name']
        course_name = request.GET.get('course_name', '')
        file_name = request.GET.get('file_name', '')

        try:
            file_path = CcFile.objects.get(teacher_name=teacher_name,course_name=course_name,file_name=file_name)\
                .file_path
        except CcFile.DoesNotExist:
            return HttpResponse(json.dumps("Can not find file!", ensure_ascii=False),
                                content_type="application/json.charset=utf-8")
        try:
            file = open(file_path, 'rb')
        except FileNotFoundError:
            return HttpResponse(json.dumps("Can not find file!", ensure_ascii=False),
                                content_type="application/json.charset=utf-8")
        response = HttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="%s"' % file_name
        return response
    if request.method == 'POST':
        return HttpResponse(json.dumps("Only can get!", ensure_ascii=False),
                            content_type="application/json.charset=utf-8")

@csrf_exempt
def getCourse(request):
    if request.method == 'POST':
        post_dict = (json.loads(request.body))
        try:
            user_id = WxUser.objects.get(uuid=post_dict['open_id']).user_id
            cc_id = CcUser.objects.get(user_id=user_id).cc_id
        except :
            cc_id = ''
        course_queryset = CcTakes.objects.filter(cc_id=cc_id)
        course_list = []
        for course in course_queryset:
            course_dict={}
            course_dict['teacher_name'] = course.teacher_name
            course_dict['course_name'] = course.course_name
            course_list.append(course_dict)
        return HttpResponse(json.dumps(course_list, ensure_ascii=False)
                            , content_type="application/json.charset=utf-8")
    if request.method == 'GET':
        return HttpResponse(json.dumps("Only can be posted!", ensure_ascii=False),
                            content_type="application/json.charset=utf-8")


'''{"data":[{"course_name":"大学英语（综合）-1","grade":77,"credit":2},{}],"avg_grade":xx,"avg_gpa":xx}'''

@csrf_exempt
def calculateGPA(grade):
    if grade > 90:
        return 4.0
    elif grade >= 85:
        return 3.7
    elif grade >= 80:
        return 3.3
    elif grade >= 76:
        return 3.0
    elif grade >= 73:
        return 2.7
    elif grade >= 70:
        return 2.3
    elif grade >= 66:
        return 2.0
    elif grade >= 63:
        return 1.7
    elif grade >=61:
        return 1.3
    elif grade == 60:
        return 1.0
    return 0.0

@csrf_exempt
def getGrade(request):
    if request.method == 'POST':
        post_dict = (json.loads(request.body))
        try:
            user_id = WxUser.objects.get(uuid=post_dict['open_id']).user_id
            urp_user = UrpUser.objects.get(user_id=user_id).urp_user
        except UrpUser.DoesNotExist:
            urp_user = ''
        result_dict = {}
        grade_list = []
        total_credit = 0
        total_grade = 0
        total_gpa = 0.00
        grade_queryset = UrpGrade.objects.filter(urp_user=urp_user)
        for grade in grade_queryset:
            grade_msg_dict = {}
            grade_msg_dict['course_name'] = grade.course_name
            grade_msg_dict['grade'] = grade.grade
            grade_msg_dict['credit'] = grade.credit
            total_credit += grade_msg_dict['credit']
            total_grade += grade_msg_dict['credit'] * grade_msg_dict['grade']
            total_gpa += grade_msg_dict['credit'] * calculateGPA(grade_msg_dict['grade'])
            grade_list.append(grade_msg_dict)
        if total_credit == 0:
            return HttpResponse(json.dumps(result_dict, ensure_ascii=False)
                                , content_type="application/json.charset=utf-8")
        result_dict["data"] = grade_list
        result_dict["avg_grade"] = total_grade/total_credit
        result_dict["avg_gpa"] = total_gpa/total_credit
        return HttpResponse(json.dumps(result_dict, ensure_ascii=False)
                            , content_type="application/json.charset=utf-8")
    if request.method == 'GET':
        return HttpResponse(json.dumps("Only can be posted!", ensure_ascii=False),
                            content_type="application/json.charset=utf-8")
