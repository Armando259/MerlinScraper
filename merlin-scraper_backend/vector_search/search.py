import os
import numpy as np
from dotenv import load_dotenv
from pymongo import MongoClient
import google.generativeai as genai

# --- Embedding klasa ---
class GeminiEmbedding:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
    def embed(self, text):
        return genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_query"
        )["embedding"]

# --- Sličnost ---
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# --- Setup ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["merlin_taskifier"]

vector_collection = db["vector_tasks"]
embedding = GeminiEmbedding(api_key=GOOGLE_API_KEY)

# --- Unesi upit ---
query = input("Upiši što tražiš: ").strip()
if not query:
    print("⛔ Upit je prazan.")
    exit(0)

# --- Embedaj upit ---
query_emb = embedding.embed(query)

# --- Povuci sve embeddinge iz baze ---
docs = list(vector_collection.find({}))

results = []
for doc in docs:
    emb = doc["embedding"]
    sim = cosine_similarity(query_emb, emb)
    results.append((sim, doc))

# --- Sortiraj po sličnosti (najprije najbliži) ---
results.sort(reverse=True, key=lambda x: x[0])

print(f"\n🔍 Najsličniji rezultati za '{query}':\n")
for i, (sim, doc) in enumerate(results[:3], 1):  # top 10
    print(f"{i}. ({sim:.3f})")
    print(f"   Kolegij:   {doc.get('kolegij', 'N/A')}")
    print(f"   Poruka:    {doc.get('text', '[nema teksta]')}\n")
