from requests_html import HTMLSession
from PIL import Image
import pytesseract,time,json
import os,django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cc_course.settings")# project_name 项目名称
django.setup()
from cc_course_app.models import UrpUser,UrpGrade

'''
session = HTMLSession()
captcha = session.get('http://zhjw.scu.edu.cn/img/captcha.jpg')
with open('test.jpg', 'wb') as fd:
    fd.write(captcha.content)
    '''

# captcha_image = Image.open('')
# opencv处理
'''
img_cv = cv2.imread('')
im = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
cv2.adaptiveThreshold(im, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 1)
cv2.imwrite('C:/Users/32838/Desktop/captcha/test1.jpg', im)
exit(0)
'''



def getCaptcha():
    captcha_image = Image.open('')
    pix = captcha_image.load()
    width = captcha_image.size[0]
    length = captcha_image.size[1]
    im = Image.new("RGB", (width, length))
    for x in range(width):
        for y in range(length):
            r, g, b = pix[x, y]
            # print(r,g,b)
            if r > 150 and g < 170 and b < 170:
                pix[x, y] = 0, 0, 0
            else:
                pix[x, y] = 255, 255, 255
            im.putpixel((x, y), pix[x, y])
    '''
    im.save('')
    img_cv = cv2.imread('')
    im = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    cv2.adaptiveThreshold(im, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 1)
    cv2.imwrite('', im)
    exit(0)
    '''
    for x in range(width):
        for y in range(length):
            if y == 0 or y == length - 1 or x == 0 or x == width - 1:
                continue
            count = 0
            if pix[x, y - 1][0] == 0:
                count += 1
            if pix[x, y + 1][0] == 0:
                count += 1
            if pix[x - 1, y][0] == 0:
                count += 1
            if pix[x + 1, y][0] == 0:
                count += 1
            if count < 1:
                # print(x,y)
                pix[x, y] = 255, 255, 255
            im.putpixel((x, y), pix[x, y])
    # im.save('' % i)
    result = pytesseract.image_to_string(im, lang='num', config="--psm 8 --oem 3 -c tessedit_"
                                                                "char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz")
    #print("result: " + result)
    # im.show()
    return result.rstrip(' ')


def login(id, password,iscrawl=False):
    global formData
    global session
    session = HTMLSession()
    formData = {'j_username': '', 'j_password': '', 'j_captcha': 'error'}
    formData['j_username'] = id
    formData['j_password'] = password
    for i in range(0,15):
        captcha = session.get('http://zhjw.scu.edu.cn/img/captcha.jpg')
        with open('', 'wb') as fd:
            fd.write(captcha.content)
        formData['j_captcha'] = getCaptcha()
        response = session.post(url='http://zhjw.scu.edu.cn/j_spring_security_check',
                                data=formData)
        serachUrl = 'http://zhjw.scu.edu.cn/student/teachingEvaluation/teachingEvaluation/search'
        getMsg = session.get(url=serachUrl, allow_redirects=False)
        code = getMsg.status_code
        if code < 300:
            # session.get(url="http://zhjw.scu.edu.cn/logout")
            if iscrawl:
                runCrawl(id)
            return True
        elif i == 14:
            return False


def runCrawl(id):
    grade_callback = session.get("http://zhjw.scu.edu.cn/student/integratedQuery"
                                 "/scoreQuery/coursePropertyScores/callback")
    grade_list = (json.loads(grade_callback.content))[0]['cjList']
    for grade in grade_list:
        try:
            UrpGrade.objects.get(course_id=grade['id']['courseNumber'],urp_user=id,
                                 exam_time=grade['id']['executiveEducationPlanNumber'])
            UrpGrade.objects.filter(course_id=grade['id']['courseNumber'], urp_user=id).update(grade=grade['courseScore'])
        except UrpGrade.DoesNotExist:
            UrpGrade.objects.create(course_id=grade['id']['courseNumber'],urp_user=id,grade=grade['courseScore'],
                                   course_name=grade['courseName'],credit=grade['credit']
                                    ,exam_time=grade['id']['executiveEducationPlanNumber'])


def timedRuning():
    user_list = UrpUser.objects.all()
    for user in user_list:
        while not login(user.urp_user, user.urp_password, True):
            pass
        print(user.urp_user+" updated")
    time.sleep(60 * 30)


'''
while True:
  timedRuning()
'''
