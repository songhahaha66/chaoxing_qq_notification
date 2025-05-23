import configparser
import http.client
import json
config = configparser.ConfigParser()
config.read("./config.ini",encoding="utf-8")
qqtoken = config.get("napcat","token")
host = config.get("napcat","host")
qq_number = config.get("qq","number")

def send_qmsg(msg):
    conn = http.client.HTTPConnection(host=host)
    payload = json.dumps({
        "user_id": qq_number,
        "message": [
            {
                "type": "text",
                "data": {
                    "text": msg
                }
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {qqtoken}"
    }
    conn.request("POST", "/send_private_msg", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

