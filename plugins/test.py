import http.client, json

conn = http.client.HTTPConnection("127.0.0.1", 3000)

payload = json.dumps({
    "group_id": 981535936,
    "message": [{
        "type": "music",
        "data": {
            "type": "custom",
            "url": "https://music.qq.com",
            "audio": "D:/Images/水瀬いのri久保ユリカ-EndlessJourney.flac",
            "title": "Endless Journey",
            "content": "少女終末旅行-EP",
            "image": "D:/Desktop/Desktop/image/少女终末旅行.jpg"
        }
    }]
})

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ETO'
}

conn.request("POST", "/send_group_msg", payload, headers)
res = conn.getresponse()
print(res.read().decode())
