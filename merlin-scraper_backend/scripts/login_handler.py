import time
import re
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from mongo_utils import save_login_to_mongo


def run():
    driver = None
    try:
        print("🔐 Otvaram browser za prijavu...")
        driver = webdriver.Chrome()
        driver.get("https://moodle.srce.hr/2024-2025/auth/simplesaml/login.php?lang=hr")
        print("➡️ Čekam da se korisnik ručno prijavi...")

        max_attempts = 60
        for attempt in range(max_attempts):
            try:
                cookies = driver.get_cookies()
            except WebDriverException:
                raise Exception("❌ Browser je zatvoren tijekom čekanja na login.")

            if any(c["name"] == "MoodleSessionmerlin2425" for c in cookies):
                print("✅ Cookie pronađen.")
                break
            print(f"⏳ Čekam login... ({attempt + 1}s)")
            time.sleep(1)
        else:
            raise Exception("❌ Cookie nije pronađen nakon 60 sekundi.")

        driver.get("https://moodle.srce.hr/2024-2025/my/")
        time.sleep(2)

        userid = None
        for attempt in range(max_attempts):
            try:
                page_source = driver.page_source
            except WebDriverException:
                raise Exception("❌ Browser je zatvoren prije pronalaska user ID-a.")

            userid_match = re.search(r'data-userid="(\d+)"', page_source)
            if userid_match:
                userid = userid_match.group(1)
                print("✅ User ID pronađen.")
                break
            print(f"⏳ Čekam da se učita user ID... ({attempt + 1}s)")
            time.sleep(1)

        if not userid:
            raise Exception("❌ User ID nije pronađen nakon 60 sekundi.")

        cookie_obj = driver.get_cookie("MoodleSessionmerlin2425")
        sess_cookie = cookie_obj["value"]

        sesskey_match = re.search(r'"sesskey":"([a-zA-Z0-9]+)"', page_source)
        sesskey = sesskey_match.group(1) if sesskey_match else None
        if not sesskey:
            raise Exception("❌ Sesskey nije pronađen.")

        driver.quit()

        login_data = {
            "cookie_name": cookie_obj["name"],
            "cookie_value": sess_cookie,
            "sesskey": sesskey,
            "userid": str(userid)
        }

        save_login_to_mongo(login_data)
        print("✅ Login podaci spremljeni u MongoDB")

        return login_data  # 🔁 ključni dodatak

    except Exception as e:
        print(f"❌ Greška: {e}")
        if driver:
            try:
                driver.quit()
            except:
                pass
        raise e


if __name__ == "__main__":
    run()
