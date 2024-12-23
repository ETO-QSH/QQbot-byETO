import re

def parse_data(data):
    lines = data.strip().split('\n')
    question_answer_dict = {}
    current_question = None
    current_answer = ''
    for line in lines:
        if not line.strip():
            continue
        if re.findall(r'^\d{1,2}\.', line):
            if current_question:
                question_answer_dict[current_question] = current_answer.strip()
            current_question = line.strip().split('.')[1]
            current_answer = ''
        else:
            current_answer += line + '\n'
    if current_question:
        question_answer_dict[current_question] = current_answer.strip()

    return question_answer_dict
