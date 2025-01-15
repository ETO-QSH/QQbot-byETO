from curl_cffi import requests
from lxml import html

response = requests.get('https://prts.wiki/w/艾雅法拉')
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
            'title': item.get('data-title') + '.wav',
            'filename': item.get('data-voice-filename').lower(),
            'voice_text': voice_text,
            'voice_base': voice_data_base
        }

    print(voice_data_items)

    voice_table_html = html.tostring(voice_data_root, encoding='unicode', pretty_print=True)
    # print(voice_table_html)

else:
    print(f'请求失败，状态码：{response.status_code}')

