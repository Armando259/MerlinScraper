import os
import re
import json
import fitz  # PyMuPDF
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from google import genai

# === Setup ===
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["merlin_taskifier"]

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai_client = genai.Client(api_key=GEMINI_API_KEY)


def extract_text_from_pdf_url(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()

    with open("temp_dinp.pdf", "wb") as f:
        f.write(response.content)

    doc = fitz.open("temp_dinp.pdf")
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    os.remove("temp_dinp.pdf")
    return text


def prompt_dinp_tasks(text: str, course_name: str) -> list:
    prompt = f"""
Na temelju sljedećeg detaljnog izvedbenog nastavnog plana (DINP) za kolegij, identificiraj sve studentske aktivnosti koje:

1. Imaju točno naveden datum (ili više njih)
2. Nose bodove (ili su dio vrednovanja kolegija)

Za svaku takvu aktivnost vrati objekt u JSON listi s poljima:

- "date": datum u formatu "dd. mm. yyyy"
- "name": kratak naziv aktivnosti (npr. "Kolokvij", "Projektna prezentacija", "Završni ispit")
- "course": naziv kolegija, ovdje: {course_name}
- "description": što student mora napraviti

⚠️ Vrati samo aktivnosti koje imaju datum i nose bodove.
⚠️ Ako je aktivnost vezana uz više datuma (npr. ispitni rokovi), stavi svaki datum kao zaseban objekt u listi.
⚠️ Ne vraćaj nikakav dodatni tekst osim ispravnog JSON.

Evo nastavnog plana:

---
{text}
"""
    response = genai_client.models.generate_content(
        model="gemini-1.5-flash", contents=prompt
    )

    match = re.search(r"\[.*\]", response.text, re.DOTALL)
    return json.loads(match.group(0)) if match else []


def run():
    pdf_entries = list(db["dinp_pdfs"].find({}))
    if not pdf_entries:
        print("⚠️ Nema spremljenih DINP PDF-ova.")
        return

    all_tasks = []

    for entry in pdf_entries:
        url = entry.get("url")
        course = entry.get("course", "Nepoznat kolegij")

        print(f"📄 Obrada: {url} ({course})")

        try:
            text = extract_text_from_pdf_url(url)
            tasks = prompt_dinp_tasks(text, course)

            for task in tasks:
                task["course"] = course

            all_tasks.extend(tasks)
            print(f"✅ Izvučeno {len(tasks)} zadataka iz: {course}")
        except Exception as e:
            print(f"⚠️ Greška kod {url}: {e}")

    if all_tasks:
        db["dinp_tasks"].delete_many({})
        db["dinp_tasks"].insert_many(all_tasks)
        print(f"💾 Uspješno spremljeno {len(all_tasks)} zadataka u MongoDB.")
    else:
        print("ℹ️ Nema zadataka za spremanje.")


if __name__ == "__main__":
    run()
