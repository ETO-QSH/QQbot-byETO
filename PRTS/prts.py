from curl_cffi import requests
from lxml import html
import json


def get_voice_info(name):
    response = requests.get(f'https://prts.wiki/w/{name}')
    if response.status_code == 200:
        tree = html.fromstring(response.content)
        voice_data_root = tree.xpath('//*[@id="voice-data-root"]')[0]
        voice_data_item = voice_data_root.xpath('.//div[@class="voice-data-item"]')
        voice_data_base = {key: value for pair in voice_data_root.get('data-voice-base').split(',') for key, value in [pair.split(':')]}
        voice_mob = '//torappu.prts.wiki/assets/audio/{voice_base}/{filename}?filename={title}'
        voice_data_items = {}
        for item in voice_data_item:
            voice_text, voice_details = {}, item.xpath('.//div[@class="voice-item-detail"]')
            for detail in voice_details:
                kind_name = detail.get('data-kind-name')
                voice_text[kind_name] = detail.text_content().strip()
            voice_data_items[item.get('data-voice-index')] = {
                'title': item.get('data-title'),
                'filename': item.get('data-voice-filename'),
                'voice_text': voice_text,
                'voice_link': {key: voice_mob.format(filename=item.get('data-voice-filename').lower(),
                               voice_base=value, title=item.get('data-title')) for key, value in voice_data_base.items()}}
        return voice_data_items
    else:
        return "ERROR"


response = requests.get('https://prts.wiki/w/干员一览')
if response.status_code == 200:
    tree = html.fromstring(response.content)  # print(html.tostring(tree, encoding='unicode', pretty_print=True))
    filter_data = tree.xpath('//*[@id="filter-data"]')[0]
    datas = {item.get('data-zh'): {key[5:]: value for key, value in item.items() if key.startswith('data-')} for item in filter_data}
    InformationDictionary = {
        item: get_voice_info(item)
        for item in datas.keys()
    }
    with open('prts.json', 'w', encoding='utf-8') as file:
        json.dump(InformationDictionary, file, indent=4)
else:
    print(f'请求失败，状态码：{response.status_code}')

