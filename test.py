import json


def read_json(JSON):
    with open(JSON, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


date = read_json("形式与政策.json")


search_string = '二十'

found_dictionaries = []

for key, items in date.items():
    for item in items:
        for i in items[item]:
            if search_string in i["Body"]:
                found_dictionaries.append({item: i})

# 打印结果
print(found_dictionaries)