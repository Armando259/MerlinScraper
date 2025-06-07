import json
import re
import html
import joblib
import os
from mongo_utils import get_notifications_by_userid, save_tasks_to_mongo


def ocisti_poruku(text):
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[-=*_]{3,}", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"[^A-Za-zČĆŽŠĐčćžšđ0-9,.!?()\- ]", "", text)
    return text


def run(userid=None):
    if not userid:
        print("❌ Nije proslijeđen userid.")
        return

    # Učitaj model i vektorizator
    model = joblib.load("models/model.pkl")
    vectorizer = joblib.load("models/vectorizer.pkl")

    # Dohvati obavijesti iz MongoDB
    data = get_notifications_by_userid(userid)
    if not data:
        print(f"⚠️ Nema obavijesti za userid {userid}")
        return

    taskovi = []
    sve_ociscene_poruke = []

    for n in data:
        subject = n.get("subject", "")
        fullmessage = n.get("fullmessage", "")

        # Izdvajanje kolegija
        match = re.search(r"\[Merlin\]\s*(.*?):", subject)
        kolegij = match.group(1).strip() if match else "Nepoznati kolegij"

        # Čišćenje poruke
        raw_message = fullmessage.split("---------------------------------------------------------------------")
        poruka = raw_message[1].strip() if len(raw_message) > 1 else fullmessage.strip()
        poruka = ocisti_poruku(poruka)
        tekst = f"{subject} {poruka}"

        # Klasifikacija
        X_vec = vectorizer.transform([tekst])
        label = int(model.predict(X_vec)[0])  # int za serijalizaciju u JSON

        # Spremljeni zadaci (label = 1)
        if label == 1:
            taskovi.append({
                "kolegij": kolegij,
                "poruka": poruka,
                "userid": userid
            })

        # Dodaj u listu svih poruka za JSON
        sve_ociscene_poruke.append({
            "kolegij": kolegij,
            "subject": subject,
            "poruka": poruka,
            "label": label,
            "userid": userid
        })

    # Spremi sve očišćene poruke s labelom u JSON fajl
   # os.makedirs("data", exist_ok=True)
    #with open(f"data/ociscene_poruke_{userid}.json", "w", encoding="utf-8") as f:
     #   json.dump(sve_ociscene_poruke, f, ensure_ascii=False, indent=2)

    # Spremi zadatke u MongoDB
    save_tasks_to_mongo(taskovi, userid)

    print(f"💾 Spremljeno {len(taskovi)} zadataka za korisnika {userid}.")
    #print(f"📂 Očišćene poruke s labelom spremljene u data/ociscene_poruke_{userid}.json")


if __name__ == "__main__":
    run(userid="261935")
