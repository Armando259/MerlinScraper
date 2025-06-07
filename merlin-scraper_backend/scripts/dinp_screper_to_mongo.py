import os
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from dotenv import load_dotenv
from pymongo import MongoClient
from gridfs import GridFS

# 🔐 Učitavanje .env varijabli
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["merlin_taskifier"]
fs = GridFS(db)

def get_login_data(userid):
    return db["logins"].find_one({"userid": str(userid)})

def get_enrolled_courses(sesskey, cookies):
    headers = {"Content-Type": "application/json"}
    api_url = f"https://moodle.srce.hr/2024-2025/lib/ajax/service.php?sesskey={sesskey}&info=core_course_get_enrolled_courses_by_timeline_classification"

    payload = [{
        "index": 0,
        "methodname": "core_course_get_enrolled_courses_by_timeline_classification",
        "args": {
            "offset": 0,
            "limit": 0,
            "classification": "all",
            "sort": "ul.timeaccess desc",
            "requiredfields": ["id", "fullname", "shortname", "showcoursecategory", "showshortname", "visible", "enddate"]
        }
    }]

    res = requests.post(api_url, headers=headers, cookies=cookies, json=payload)
    res.raise_for_status()
    return res.json()[0]["data"]["courses"]

def get_dinp_links(view_url, cookies):
    res = requests.get(view_url, cookies=cookies)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    links = []
    for tag in soup.find_all("a", onclick=True):
        link_text = tag.get_text(strip=True).lower()
        if "dinp" in link_text or "izvedbeni" in link_text:
            match = re.search(r"window\.open\('([^']+redirect=1)'", tag['onclick'])
            if match:
                links.append(match.group(1))
    return links

def scrape_dinp_run(userid):
    login_data = get_login_data(userid)
    if not login_data:
        raise ValueError("Nema login podataka.")

    sesskey = login_data["sesskey"]
    cookies = {login_data["cookie_name"]: login_data["cookie_value"]}
    if "token" in login_data:
        cookies["SimpleSAMLAuthToken"] = login_data["token"]

    courses = get_enrolled_courses(sesskey, cookies)
    count = 0

    for course in courses:
        course_name = course["fullname"].strip()
        view_url = course.get("viewurl")
        if not view_url:
            continue

        links = get_dinp_links(view_url, cookies)
        for link in links:
            try:
                res = requests.get(link, cookies=cookies, timeout=10, allow_redirects=True)
                res.raise_for_status()

                file_name = unquote(res.url.split("/")[-1].split("?")[0])
                if not file_name.lower().endswith(".pdf"):
                    print(f"⏩ Preskočeno (nije PDF): {file_name}")
                    continue

                if fs.exists({"filename": file_name, "user_id": userid}):
                    print(f"ℹ️ Već postoji: {file_name}")
                    continue

                fs.put(res.content, filename=file_name, user_id=userid, course=course_name)
                print(f"💾 Spremljen: {file_name}")
                count += 1

            except Exception as e:
                print(f"❌ Greška za link {link} → {e}")

    print(f"✅ Ukupno spremljeno PDF-ova: {count}")

if __name__ == "__main__":
    scrape_dinp_run("userid")
