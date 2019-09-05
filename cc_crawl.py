

from requests_html import HTMLSession
import re,time

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cc_course.settings")# project_name 项目名称
django.setup()
from cc_course_app.models import  CcHomework,CcExam,CcUser,CcTakes


def runCrawl(userid,password):
    login_form = {'IDToken0': '', 'IDToken1': '', 'IDToken2': '', 'IDButton': 'Login',
                  'goto': 'aHR0cDovL2NjLnNjdS5lZHUuY24vRzJTL1Nob3dzeXN0ZW0vZG9jaGVja2NhLmFzcHg=', 'encoded': 'true',
                  'gx_charset': 'UTF-8'}
    domain = 'http://cc.scu.edu.cn'
    login_form['IDToken1'] = userid
    login_form['IDToken2'] = password
    session = HTMLSession()
    session.post(url='http://ids.scu.edu.cn/amserver/UI/Login', data=login_form)
    index = session.get(url='http://cc.scu.edu.cn/G2S/MySpace/IndexStudent.aspx')
    teacher_list = index.html.xpath('//*[@id="ctl00_ContentPlaceHolder1_UCStudentCourse1_divMultiCourse"]'
                                    '/div')

    for teacher in teacher_list:
        # print(teacher.xpath("//*[contains(@class,'AligntoLeft PL10 Width80')]/div[2]/label/@title")[0])
        course_name = str((teacher.xpath("//*[contains(@class,'AligntoLeft PL10 Width80')]/div[1]/label/@title"))[0])
        teacher_name = str((teacher.xpath("//*[contains(@class,'AligntoLeft PL10 Width80')]/div[2]/label/@title"))[0])
        # print(teacher_name)
        try:
            CcTakes.objects.get(cc_id=userid,course_name=course_name,teacher_name=teacher_name)
        except CcTakes.DoesNotExist:
            CcTakes.objects.create(cc_id=userid, course_name=course_name,teacher_name=teacher_name)
    # space_url = domain+r.html.xpath('//*[@id="ctl00_divOnLogin"]/div/div/a[1]/@href',first=True)
    view_state = index.html.xpath('//*[@id="__VIEWSTATE"]/@value')
    view_state_generator = index.html.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value')
    # print(r.html.xpath('//*[@id="__VIEWSTATE"]/@value'))
    # print(r.html.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value'))
    course_list = index.html.xpath('//*[@id="ctl00_ContentPlaceHolder1_UCStudentCourse1_divMultiCourse"]'
                                   '/div/div[2]/div[5]/input/@onclick')
    for course in course_list:
        course_id = (re.findall("GoWebsite\('(.*)'\)", course))[0]
        course_form = {'__EVENTTARGET': '', '__EVENTARGUMENT': '', '__VIEWSTATE': view_state,
                       '__VIEWSTATEGENERATOR':view_state_generator,
                       'ctl00$ContentPlaceHolder1$UCStudentCourse1$hidWebSiteID': course_id,
                       'ctl00$ContentPlaceHolder1$UCStudentCourse1$btnGoStudentWebsite': 'Button'}
        session.post(url='http://cc.scu.edu.cn/G2S/MySpace/IndexStudent.aspx', data=course_form)
        homework_index = session.get(url='http://cc.scu.edu.cn/G2S/StudentSpace/Homework/ExplorerRuning.aspx')
        course_name = (homework_index.html.xpath("//*[@id='Div_content']/div[2]/div/div[2]/div[1]/span[1]/a/@title"))[0]
        print(course_name)

        homework_list = homework_index.html.xpath("//*[@class='gridview_tl']/tr[contains(@id,'gvHomeWorkList')]")
        #print(homework_list)
        for homework in homework_list:
            try:
                #print(homework)
                pattern = re.compile(r'[^\u4e00-\u9fa5]')
                #print((homework.xpath("//div[contains(@id,'status')]/text()"))[0])
                homework_status = re.sub(pattern, '', str((homework.xpath("//div[contains(@id,'status')]/text()"))[0]))
                homework_name = str((homework.xpath("//td[3]/a/@title"))[0])
                homework_type = re.sub(pattern, '', str((homework.xpath("//td[4]/text()"))[0]))
                # homework_type = homework.xpath("//td[4]")
                homework_begintime = str((homework.xpath("//td[5]/text()"))[0])
                homework_endtime = str((homework.xpath("//td[6]/text()"))[0])
                homework_finishnum = str((homework.xpath("//*[contains(@id,'lblSubmitCount')]/text()"))[0])
                homework_handtime = str((homework.xpath("//td[7]/text()"))[0])
                print(homework_status+" "+homework_name+" "+homework_type+" "+homework_begintime+" "+homework_endtime +
                    " "+homework_finishnum+" "+homework_handtime)
                try:
                    CcHomework.objects.get(cc_id=userid,course_name=course_name,name=homework_name)
                    CcHomework.objects.filter(name=homework_name).\
                        update(state=homework_status,hand_time=homework_handtime,finish_num=homework_finishnum,
                               type=homework_type,begin_time=homework_begintime,end_time=homework_endtime)
                except CcHomework.DoesNotExist:
                    CcHomework.objects.create(cc_id=userid,course_name=course_name,name=homework_name,
                                              state=homework_status, hand_time=homework_handtime,
                                              finish_num=homework_finishnum,
                                              type=homework_type, begin_time=homework_begintime,
                                              end_time=homework_endtime)
            except IndexError:
                continue
        exam_index = session.get(url='http://cc.scu.edu.cn/G2S/StudentSpace/Exam/ExplorerRuning.aspx')
        exam_list = exam_index.html.xpath("//table/*[contains(@id,'gvExamList')]")
        for exam in exam_list:
            pattern = re.compile(r'[^\u4e00-\u9fa5]')
            exam_status = re.sub(pattern, '', str(((exam.xpath("//div[contains(@id,'Status')]/text()"))[0])))
            exam_name = str((exam.xpath("//td[3]/div/a/@title"))[0])
            exam_type = re.sub(pattern, '', str((exam.xpath("//td[4]/text()"))[0]))
            # homework_type = homework.xpath("//td[4]")
            exam_begintime = str((exam.xpath("//td[5]/text()"))[0])
            exam_endtime = str((exam.xpath("//td[6]/text()"))[0])
           # exam_finishnum = str((exam.xpath("//*[contains(@id,'lblSubmitCount')]/text()"))[0])
            exam_handtime = str((exam.xpath("//td[7]/text()"))[0])
            try:
                CcExam.objects.get(cc_id=userid,course_name=course_name, name=exam_name)
                CcExam.objects.filter(course_name=course_name, name=exam_name). \
                    update(state=exam_status, hand_time=exam_handtime,
                           type=exam_type, begin_time=exam_begintime, end_time=exam_endtime)
            except CcExam.DoesNotExist:
                CcExam.objects.create(cc_id=userid,course_name=course_name, name=exam_name,
                                          state=exam_status, hand_time=exam_handtime,
                                          type=exam_type, begin_time=exam_begintime,
                                          end_time=exam_endtime)
            print(exam_status + " " + exam_name + " " + exam_type + " " + exam_begintime + " " + exam_endtime + " " + exam_handtime)


def timedRuning():
    user_list = CcUser.objects.all()
    for user in user_list:
        print(user.cc_id)
        runCrawl(user.cc_id, user.cc_password)
    time.sleep(60*30)

#timedRuning()

'''
while True:
    timedRuning()
'''