import os
from dotenv import load_dotenv
from pymongo import MongoClient
import google.generativeai as genai

def vektoriziraj_sve_taskove():

    # --- Embedding klasa ---
    class GeminiEmbedding:
        def __init__(self, api_key: str):
            genai.configure(api_key=api_key)
        def embed(self, text):
            return genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )["embedding"]

    # --- Setup ---
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(MONGO_URI)
    db = client["merlin_taskifier"]

    source_collection = db["tasks"]   # <-- OVDJE promijeni ako treba!
    vector_collection = db["vector_tasks"]

    # --- OVDJE DODAJ UNIQUE INDEX ---
    try:
        vector_collection.create_index("task_id", unique=True)
    except Exception as e:
        print(f"⚠️ Nije moguće napraviti unique index (možda imaš duplikate): {e}")

    embedding = GeminiEmbedding(api_key=GOOGLE_API_KEY)

    # --- Povuci sve taskove iz baze ---
    tasks = list(source_collection.find({}))

    to_insert = []
    for task in tasks:
        text = f"{task.get('kolegij', '')}: {task.get('poruka', '')}"
        if not text:
            continue
        emb = embedding.embed(text)
        doc = {
            "text": text,
            "embedding": emb,
            "userid": str(task.get("userid")) if "userid" in task else None,
            "task_id": str(task.get("_id")),
            "kolegij": str(task.get("kolegij")) if task.get("kolegij") else ""
        }
        to_insert.append(doc)

    # --- Insert (preskače duplikate) ---
    if to_insert:
        try:
            vector_collection.insert_many(to_insert, ordered=False)
            print(f"✅ Spremljeno {len(to_insert)} embeddinga u vector_tasks!")
        except Exception as e:
            print(f"⚠️ Neki embeddingi nisu spremljeni (mogući duplikati): {e}")
    else:
        print("⚠️ Nema taskova za spremiti.")

if __name__ == "__main__":
    vektoriziraj_sve_taskove()
