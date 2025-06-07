import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote

# ---- Config ----
SESSKEY = "eEmaPFSr1G"
COOKIES = {
    "MoodleSessionmerlin2425": "3qpvs442c91ueesvame056qo9j",
    "SimpleSAMLSessionID": "_bb3c1138555fc4ecfd72ddfa01f7afc15177348f3d",
    "SimpleSAMLAuthToken": "e217d18975f5ba8bac83f84b6219f4fe",
}
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

API_URL = f"https://moodle.srce.hr/2024-2025/lib/ajax/service.php?sesskey={SESSKEY}&info=core_course_get_enrolled_courses_by_timeline_classification"

HEADERS = {
    "Content-Type": "application/json"
}

PAYLOAD = [{
    "index": 0,
    "methodname": "core_course_get_enrolled_courses_by_timeline_classification",
    "args": {
        "offset": 0,
        "limit": 0,
        "classification": "all",
        "sort": "ul.timeaccess desc",
        "customfieldname": "",
        "customfieldvalue": "",
        "requiredfields": ["id", "fullname", "shortname", "showcoursecategory", "showshortname", "visible", "enddate"]
    }
}]

session = requests.Session()


def get_enrolled_courses():
    print("📡 Dohvaćam popis kolegija...")
    res = session.post(API_URL, headers=HEADERS, cookies=COOKIES, json=PAYLOAD)
    res.raise_for_status()
    try:
        courses = res.json()[0]['data']['courses']
        print(f"✅ Pronađeno kolegija: {len(courses)}")
        return courses
    except (KeyError, IndexError) as e:
        print(f"❌ Greška pri parsiranju kolegija: {e}")
        print("ℹ️ Odgovor:")
        print(res.json())
        return []


def get_dinp_links_from_course(view_url):
    res = session.get(view_url, cookies=COOKIES)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')

    links = []
    for tag in soup.find_all('a', onclick=True):
        anchor_text = tag.get_text(strip=True).lower()
        if "dinp" in anchor_text or "detaljni izvedbeni nastavni plan" in anchor_text:
            match = re.search(
                r"window\.open\('([^']+redirect=1)'", tag['onclick'])
            if match:
                links.append(match.group(1))
    return links


def download_dinp(view_resource_url):
    try:
        print(f"🔍 Pokušavam preuzeti: {view_resource_url}")
        res = session.get(view_resource_url, cookies=COOKIES,
                          allow_redirects=True, timeout=10)
        res.raise_for_status()
        final_url = res.url

        file_name = unquote(final_url.split('/')[-1].split('?')[0])
        if not file_name.lower().endswith('.pdf'):
            print(f"⛔ {file_name} nije PDF — preskačem.")
            return False

        file_path = os.path.join(DOWNLOAD_DIR, file_name)
        if os.path.exists(file_path):
            print(f"📁 Već postoji: {file_name} — preskačem.")
            return False

        with open(file_path, 'wb') as f:
            f.write(res.content)
        print(f"✅ Preuzeto: {file_name}")
        return True

    except Exception as e:
        print(f"❌ Greška: {e}")
        return False


def main():
    courses = get_enrolled_courses()
    for course in courses:
        name = course['fullname'].strip()
        if name.lower() == "referada":
            print(f"⏭️ Preskačem predmet: {name}")
            continue

        print(f"\n🏫 {name}")
        view_url = course.get('viewurl')
        if not view_url:
            print("⚠️ Nema URL-a za predmet.")
            continue

        print(f"🌐 Posjećujem: {view_url}")
        links = get_dinp_links_from_course(view_url)
        print(f"🔗 Relevantni linkovi: {len(links)}")

        downloads = sum(download_dinp(link) for link in links)
        if downloads == 0:
            print("ℹ️ Nema novih DINP dokumenata za preuzimanje.")


if __name__ == "__main__":
    main()
