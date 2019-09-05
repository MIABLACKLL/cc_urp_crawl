import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cc_course.settings")# project_name 项目名称
django.setup()
from cc_course_app.models import  CcHomework,CcExam,CcUser,CcTakes,UrpGrade,UrpUser

urp_user="2017141463045"
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
result_dict["data"] = grade_list
result_dict["avg_grade"] = total_grade/total_credit
result_dict["avg_gpa"] = total_gpa/total_credit

print(result_dict)