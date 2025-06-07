import os
import re
import json
import fitz
from dotenv import load_dotenv
from pymongo import MongoClient
from gridfs import GridFS
from google import genai

# 🔐 Učitavanje .env
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = MongoClient(MONGO_URI)
db = client["merlin_taskifier"]
fs = GridFS(db)
genai_client = genai.Client(api_key=GEMINI_API_KEY)

def extract_pdf_text(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

def prompt_dinp_tasks(text, course_name):
    prompt = f"""
Na temelju sljedećeg detaljnog izvedbenog nastavnog plana (DINP) za kolegij "{course_name}", identificiraj sve studentske aktivnosti koje:
1. Imaju točno naveden datum
2. Nose bodove

Vrati JSON listu objekata s poljima:
- "date": datum u formatu "dd. mm. yyyy"
- "name": naziv aktivnosti
- "course": naziv kolegija
- "description": što student mora napraviti

⚠️ Vrati samo JSON — bez dodatnih komentara.

---
{text}
"""
    response = genai_client.models.generate_content(
        model="gemini-1.5-flash", contents=prompt
    )
    match = re.search(r"\[.*\]", response.text, re.DOTALL)
    return json.loads(match.group(0)) if match else []

def parse_dinp_run(userid):
    pdfs = fs.find({"user_id": userid})
    all_tasks = []

    for pdf in pdfs:
        try:
            course_name = pdf.course
            pdf_bytes = pdf.read()
            text = extract_pdf_text(pdf_bytes)
            tasks = prompt_dinp_tasks(text, course_name)
            for t in tasks:
                t["user_id"] = userid
            all_tasks.extend(tasks)
        except Exception as e:
            print(f"❌ Greška kod {pdf.filename}: {e}")

    if all_tasks:
        db["dinp_tasks"].delete_many({"user_id": userid})
        db["dinp_tasks"].insert_many(all_tasks)
        print(f"✅ Spremljeno {len(all_tasks)} zadataka u MongoDB.")
    else:
        print("⚠️ Nema zadataka za spremanje.")

if __name__ == "__main__":
    parse_dinp_run("userid")
