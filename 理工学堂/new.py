import json
import requests

base_url = "http://lgxt.wutp.com.cn/api"
headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded',
}

session = requests.Session()

with open('高等数学.json', 'r', encoding='utf-8') as file:
    InformationDictionary = json.load(file)

def login(username, password):
    login_url = f"{base_url}/login"
    data = {'loginName': username, 'password': password}
    try:
        response = session.post(login_url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result['code'] == 0:
            token = result['data']
            headers['Authorization'] = token
            session.headers.update({'Authorization': token})
            return True, "欢迎回来！"
        else:
            return False, f"登录失败：{result['msg']}"
    except requests.exceptions.RequestException as e:
        return False, f"网络错误：{e}"

def get_my_courses():
    my_courses_url = f"{base_url}/myCourses"
    try:
        response = session.post(my_courses_url, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result['code'] == 0:
            courses = result['data']
            return True, courses
        else:
            return False, f"获取课程列表失败：{result['msg']}"
    except requests.exceptions.RequestException as e:
        return False, f"网络错误：{e}"

def get_course_works(course_id):
    my_course_works_url = f"{base_url}/myCourseWorks"
    data = {'courseId': course_id}
    try:
        response = session.post(my_course_works_url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result['code'] == 0:
            works = result['data']
            return True, works
        else:
            return False, f"获取课程作业失败：{result['msg']}"
    except requests.exceptions.RequestException as e:
        return False, f"网络错误：{e}"

def get_questions(work_id):
    show_questions_url = f"{base_url}/showQuestions"
    data = {'workId': work_id}
    try:
        response = session.post(show_questions_url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result['code'] == 0:
            questions = result['data']
            return True, questions
        else:
            return False, f"获取题目失败：{result['msg']}"
    except requests.exceptions.RequestException as e:
        return False, f"网络错误：{e}"

def collect_all_questions(work_id, max_iterations=100):
    collected_questions = {}
    no_new_questions_count = 0
    for i in range(max_iterations):
        success, questions = get_questions(work_id)
        if success:
            new_question_found = False
            for question in questions:
                question_id = question.get('id')
                if question_id not in collected_questions:
                    collected_questions[question_id] = question
                    new_question_found = True
            if new_question_found:
                no_new_questions_count = 0
            else:
                no_new_questions_count += 1
                if no_new_questions_count >= 10:
                    break
        else:
            break
    return collected_questions

def save_questions_to_word(collected_questions, work_name):
    if work_name not in InformationDictionary:
        InformationDictionary[work_name] = {}
        sorted_question_ids = sorted(collected_questions.keys(), key=lambda x: int(x))
        for idx, question_id in enumerate(sorted_question_ids):
            question = collected_questions[question_id]
            InformationDictionary[work_name][question_id] = [question.get('name', 'N/A'), question.get('answer', 'N/A')]

login_state, login_result = login('2373204754', '******')

courses = {}
courses_state, courses_result = get_my_courses()
for item in courses_result:
    courses[item['bookName']] = item['courseId']
print(courses)

works = {}
works_state, works_result = get_course_works('42')
for item in works_result:
    works[item['workName']] = item['workId'], item['times'], item['grade']
print(works)

save_questions_to_word(collect_all_questions(598), "第6章网上作业")
with open('高等数学.json', 'w', encoding='utf-8') as file:
    json.dump(InformationDictionary, file, indent=4)
