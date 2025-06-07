import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

# Uvoz naprednih modela (ako su dostupni)
try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier = None

try:
    from lightgbm import LGBMClassifier
except ImportError:
    LGBMClassifier = None

def load_data(path="data/training_data1.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts = [x["text"] for x in data]
    labels = [x["label"] for x in data]
    return texts, labels

def evaluate_models(X_train, X_test, y_train, y_test):
    models = {
        "Calibrated SVM": CalibratedClassifierCV(LinearSVC(class_weight="balanced"))
    }

    if XGBClassifier:
        models["XGBoost"] = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    if LGBMClassifier:
        models["LightGBM"] = LGBMClassifier()

    results = []

    for name, model in models.items():
        print(f"\n🔍 Evaluating: {name}")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        print(classification_report(y_test, y_pred, digits=3))
        print("Confusion Matrix:")
        print(pd.DataFrame(confusion_matrix(y_test, y_pred),
                           columns=["Pred 0", "Pred 1"],
                           index=["True 0", "True 1"]))

        scores = classification_report(y_test, y_pred, output_dict=True)
        results.append({
            "Model": name,
            "Accuracy": scores["accuracy"],
            "F1_macro": scores["macro avg"]["f1-score"]
        })

    return pd.DataFrame(results).sort_values(by="F1_macro", ascending=False)

def main():
    texts, labels = load_data()

    X_train_texts, X_test_texts, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    vectorizer = TfidfVectorizer(max_features=1000)
    X_train = vectorizer.fit_transform(X_train_texts)
    X_test = vectorizer.transform(X_test_texts)

    results_df = evaluate_models(X_train, X_test, y_train, y_test)

    print("\n🏁 Usporedba svih modela:")
    print(results_df)

if __name__ == "__main__":
    main()
