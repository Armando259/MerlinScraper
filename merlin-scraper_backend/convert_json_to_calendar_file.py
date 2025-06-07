import os
from datetime import datetime
from ics import Calendar, Event
from pymongo import MongoClient
from dotenv import load_dotenv

# 🔐 Učitavanje .env
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["merlin_taskifier"]

def parse_date(date_str: str) -> datetime:
    """Pokušava parsirati datum u više formata."""
    date_str = date_str.strip()
    possible_formats = ["%d. %m. %Y", "%d.%m.%Y", "%d. %m.", "%d.%m."]
    for fmt in possible_formats:
        try:
            date = datetime.strptime(date_str, fmt)
            if "%Y" not in fmt:
                date = date.replace(year=datetime.now().year)
            return date
        except ValueError:
            continue
    raise ValueError(f"Ne mogu parsirati datum: '{date_str}'")

def generate_ics_for_user(userid: str, output_path: str = "studentski_raspored.ics"):
    tasks = list(db["dinp_tasks"].find({"user_id": str(userid)}))
    calendar = Calendar()

    for item in tasks:
        try:
            name = item.get("name") or item.get("naame") or "Zadatak"
            description = item.get("description", "Nema opisa")
            course = item.get("course", "Nepoznat kolegij")

            date_obj = parse_date(item["date"])

            event = Event()
            event.name = f"{name} - {course}"
            event.description = description
            event.begin = date_obj.strftime("%Y-%m-%d")
            event.make_all_day()
            calendar.events.add(event)

        except Exception as e:
            print(f"⚠️ Greška u zadatku: {item} → {e}")

    with open(output_path, "wb") as f:
        f.write(calendar.serialize().encode("utf-8"))

    print(f"✅ .ics datoteka generirana: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_ics_for_user("261935")
