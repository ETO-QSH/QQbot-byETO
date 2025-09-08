import json
from http.client import HTTPConnection


audio = "https://raw.githubusercontent.com/ETO-QSH/QQbot-byETO/refs/heads/main/links/水瀬いのり%20久保ユリカ%20-%20Endless%20Journey.flac"
image = "https://raw.githubusercontent.com/ETO-QSH/QQbot-byETO/refs/heads/main/links/少女终末旅行_1x1.jpg"

payload = json.dumps({
    "group_id": 981535936,
    "message": [{
        "type": "music",
        "data": {
            "type": "custom",
            "url": "https://github.com/ETO-QSH/QQbot-byETO",
            "audio": audio,
            "title": "Endless Journey",
            "content": "少女終末旅行-EP",
            "image": image
        }
    }]
})

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ETO'
}

conn = HTTPConnection("127.0.0.1", 3000)
conn.request("POST", "/send_group_msg", payload, headers)
res = conn.getresponse()
print(res.read().decode())
