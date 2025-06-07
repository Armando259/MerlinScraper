from flask import Flask, request, session, jsonify, send_file
from flask_cors import CORS
import os
import numpy as np
from pymongo import MongoClient
import google.generativeai as genai
from dotenv import load_dotenv

# Ostali importi
from scripts.login_handler import run as login_handler_run
from scripts.fetch_notifications import run as fetch_notifications_run
from scripts.detect_tasks import run as classifier_run
from scripts.taskify import run as taskifier_run
from scripts.dinp_parser_mongo import parse_dinp_run
from scripts.dinp_screper_to_mongo import scrape_dinp_run
from convert_json_to_calendar_file import generate_ics_for_user
from mongo_utils import get_dinp_tasks_by_userid
from vector_search.index_tasks import vektoriziraj_sve_taskove

from mongo_utils import (
    save_student_tasks_to_mongo,
    get_student_tasks_by_userid,
    get_login_by_userid
)

# -- Helper funkcije --
def get_userid_from_session():
    return session.get("userid")

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    if a.shape != b.shape:
        # Neusporedivi vektori, vrati nisku sličnost
        return -1.0
    num = np.dot(a, b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(num) / float(denom)

class GeminiEmbedding:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
    def embed(self, text):
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return result["embedding"]

# -- Flask app setup --
app = Flask(__name__)
app.secret_key = "tajni_kljuc"
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5173"],
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"],
)

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response

# -- ROUTES --

@app.route("/login")
def login():
    try:
        login_data = login_handler_run()
        if not login_data or "userid" not in login_data:
            return jsonify({"error": "Login nije uspio ili nema userid."}), 500

        userid = str(login_data["userid"])
        session["userid"] = userid
        print("Id korisnika je", userid)
        return jsonify({"message": "Uspješna prijava", "userid": userid})
    except Exception as e:
        print(f"❌ Greška prilikom logina: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/generate_tasks", methods=["GET"])
def generate_tasks():
    try:
        limit = int(request.args.get("limit", 50))
        userid = session.get("userid")
        if not userid:
            return jsonify({"error": "Nema aktivnog korisnika u sesiji."}), 401

        # Pokretanje koraka
        fetch_notifications_run(userid=userid, limit=limit)
        classifier_run(userid=userid)
        taskifier_run(userid=userid)
        vektoriziraj_sve_taskove()

        tasks = get_student_tasks_by_userid(userid)
        return jsonify({
            "status": "success",
            "message": f"Generirano {len(tasks)} zadataka (limit: {limit}).",
            "count": len(tasks),
            "tasks": tasks
        }), 200

    except Exception as e:
        print(f"❌ Greška u /generate_tasks: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/tasks", methods=["GET"])
def get_all_tasks():
    try:
        userid = session.get("userid")
        if not userid:
            return jsonify({"error": "Niste prijavljeni."}), 401
        tasks = get_student_tasks_by_userid(userid)
        return jsonify({"status": "success", "tasks": tasks}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/fetch")
def fetch_notifications():
    userid = session.get("userid")
    print(f"📦 [FETCH] USERID iz sesije: {userid}")
    if not userid:
        return jsonify({"error": "Korisnik nije prijavljen."}), 401

    login_data = get_login_by_userid(userid)
    if not login_data:
        print(f"❌ [FETCH] Nema login podataka za korisnika {userid} u MongoDB.")
        return jsonify({"error": "Nema login podataka za korisnika."}), 404

    fetch_notifications_run(userid=userid, limit=20)
    return jsonify({"message": f"Obavijesti za userid={userid} spremljene."})

@app.route("/process_dinp", methods=["GET"])
def process_dinp():
    userid = session.get("userid")
    if not userid:
        return jsonify({"error": "Korisnik nije prijavljen."}), 401

    try:
        print(f"👉 Pokrećem DINP scrape za userid {userid}")
        scrape_dinp_run(userid)
        print(f"👉 Pokrećem DINP parsing za userid {userid}")
        parse_dinp_run(userid)
        return jsonify({"message": "DINP obrada završena!"}), 200
    except Exception as e:
        print(f"❌ Greška u /process_dinp: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/download_calendar", methods=["GET"])
def download_calendar():
    userid = session.get("userid")
    if not userid:
        return jsonify({"error": "Nema prijavljenog korisnika."}), 401
    try:
        ics_path = generate_ics_for_user(userid)
        return send_file(
            ics_path,
            as_attachment=True,
            download_name="studentski_raspored.ics",
            mimetype="text/calendar"
        )
    except Exception as e:
        print(f"❌ Greška pri generiranju kalendara: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/dinp_tasks", methods=["GET"])
def get_dinp_tasks():
    userid = get_userid_from_session()
    if not userid:
        return jsonify({"error": "Niste prijavljeni"}), 401
    tasks = get_dinp_tasks_by_userid(userid)
    return jsonify({"tasks": tasks})

@app.route("/vector_search", methods=["POST"])
def vector_search():
    # 🔒 Autentikacija
    userid = session.get("userid")
    if not userid:
        return jsonify({"error": "Niste prijavljeni."}), 401

    # ⌨️ Uzimanje upita
    data = request.json
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Upit je prazan."}), 400

    # --- Embedding upita ---
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    embedding = GeminiEmbedding(api_key=GOOGLE_API_KEY)
    query_emb = embedding.embed(query)

    # --- Povuci embeddinge iz vektorske kolekcije ---
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    db = client["merlin_taskifier"]
    vector_collection = db["vector_tasks"]

    docs = list(vector_collection.find({"userid": userid}))

    results = []
    for doc in docs:
        emb = doc["embedding"]
        sim = cosine_similarity(query_emb, emb)
        results.append({
            "similarity": sim,
            "text": doc.get("text", ""),
            "kolegij": doc.get("kolegij", ""),
            "task_id": doc.get("task_id", ""),
            "userid": doc.get("userid", "")
        })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    top_results = results[:3]




    return jsonify({
        "success": True,
        "query": query,
        "count": len(top_results),
        "results": [
            {
                "rank": i+1,
                "similarity": round(result["similarity"], 3),
                "text": result["text"],
                "course": result.get("kolegij", ""),
                "task_id": result.get("task_id", "")
            }
            for i, result in enumerate(top_results)
        ],
        "message": f"Prikazujem top {len(top_results)} rezultata za upit: '{query}'."
    }), 200


if __name__ == "__main__":
    load_dotenv()
    app.run(debug=True, port=3000, host="0.0.0.0")
