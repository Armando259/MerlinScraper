import json
import requests
from mongo_utils import get_login_by_userid, save_notifications_to_mongo

def run(userid, limit=20):
    userid = str(userid)  # 🔒 Forsiraj string za sigurnost
    login = get_login_by_userid(userid)
    if not login:
        print(f"❌ Nema login podataka za korisnika {userid} u MongoDB.")
        return False

    url = f"https://moodle.srce.hr/2024-2025/lib/ajax/service.php?sesskey={login['sesskey']}&info=message_popup_get_popup_notifications"
    payload = json.dumps([{
        "index": 0,
        "methodname": "message_popup_get_popup_notifications",
        "args": {
            "limit": limit,
            "offset": 0,
            "useridto": userid
        }
    }])

    headers = {
        "Content-Type": "application/json",
        "Cookie": f"{login['cookie_name']}={login['cookie_value']}"
    }

    print(f"🔍 Dohvaćam obavijesti za userid {userid}...")
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code != 200:
        print("❌ Greška pri dohvaćanju podataka:", response.status_code)
        print(response.text)
        return False

    data = response.json()[0]["data"]["notifications"]

    # Dodaj user_id u svaku notifikaciju
    for d in data:
        d["userid"] = userid

    # 🔒 Spremi u MongoDB
    save_notifications_to_mongo(userid, data)

   
if __name__ == "__main__":
    run(userid="261935", limit=20)
