import json
import joblib
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import os

# Učitaj podatke
with open("data/training_data1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [x["text"] for x in data]
labels = [x["label"] for x in data]

# Podjela (opcionalno – za ravnotežu, trenira se na cijelom skupu)
X_train_texts, _, y_train, _ = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

# Vektorizacija
vectorizer = TfidfVectorizer(max_features=1000)
X_train = vectorizer.fit_transform(X_train_texts)

# Treniranje SVM modela
model = LinearSVC(class_weight="balanced")
model.fit(X_train, y_train)

# Osiguraj direktorij
os.makedirs("models", exist_ok=True)

# Spremi model i vektorizator
joblib.dump(model, "models/model.pkl")
joblib.dump(vectorizer, "models/vectorizer.pkl")

print("✅ Model i vektorizator su spremljeni.")
