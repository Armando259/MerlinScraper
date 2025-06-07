import json
import re
import os
from google import genai
from dotenv import load_dotenv
from mongo_utils import get_tasks_by_userid, save_student_tasks_to_mongo

def run(userid=None):
    if not userid:
        print("❌ Nije proslijeđen userid.")
        return

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY nije definiran.")
        return

    client = genai.Client(api_key=api_key)

    # Dohvati zadatke iz MongoDB (tasks kolekcija)
    tasks = get_tasks_by_userid(userid)
    if not tasks:
        print(f"⚠️ Nema zadataka za korisnika {userid}")
        return

    rezultati = []

    for task in tasks:
        poruka = task.get("poruka", "")

        prompt = f"""
        Ti si student i stigla ti je ova obavijest:
        "{poruka}"

        Cilj ti je zapisati si što bolje zadatak kako bi kasnije imao pregled svojih obaveza i znao kako ih izvršiti.

        Vrati JSON objekt s:
        {{
            "task_name": "...",
            "task_description": "...",
            "difficulty": "easy" | "medium" | "hard"
        }}

        Vrati samo ispravan JSON objekt bez objašnjenja.
        """

        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash", contents=prompt
            )
            match = re.search(r"\{.*?\}", response.text, re.DOTALL)
            if match:
                json_obj = json.loads(match.group(0))
            else:
                raise ValueError("Nije pronađen JSON")

        except Exception as e:
            print(f"⚠️ Greška: {e}")
            json_obj = {
                "task_name": "Nepoznato",
                "task_description": poruka[:150] + "...",
                "difficulty": "medium",
            }

        json_obj["userid"] = userid
        rezultati.append(json_obj)

    # Spremi u MongoDB (student_tasks kolekcija)
    save_student_tasks_to_mongo(rezultati, userid=userid)

if __name__ == "__main__":
    run(userid="261935")
