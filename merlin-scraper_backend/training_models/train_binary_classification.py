import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC

# 1. Učitavanje podataka
with open("data/training_data1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [x["text"] for x in data]
labels = [x["label"] for x in data]

X_train_texts, X_test_texts, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

# 2. Vektorizacija teksta
vectorizer = TfidfVectorizer(max_features=1000)
X_train = vectorizer.fit_transform(X_train_texts)
X_test = vectorizer.transform(X_test_texts)

# 3. Lista modela za testiranje
models = {
    "Logistic Regression": LogisticRegression(class_weight="balanced"),
    "Naive Bayes": MultinomialNB(),
    "Random Forest": RandomForestClassifier(class_weight="balanced", random_state=42),
    "Linear SVM": LinearSVC(class_weight="balanced")
}

# 4. Evaluacija
results = []

for name, model in models.items():
    print(f"\n🔍 Evaluating: {name}")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    report = classification_report(y_test, y_pred, output_dict=True)
    f1_macro = report["macro avg"]["f1-score"]
    accuracy = report["accuracy"]

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "F1_macro": f1_macro
    })

    print(classification_report(y_test, y_pred, digits=3))
    print("Confusion Matrix:")
    print(pd.DataFrame(confusion_matrix(y_test, y_pred),
                       columns=["Pred 0", "Pred 1"],
                       index=["True 0", "True 1"]))

# 5. Prikaz usporedbe
df_results = pd.DataFrame(results).sort_values(by="F1_macro", ascending=False)
print("\n🏆 Rezultati usporedbe modela:")
print(df_results)
