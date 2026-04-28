import os
import json
import joblib
import nltk
from nltk.stem.porter import PorterStemmer
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure NLTK data is downloaded
nltk.download('punkt_tab', quiet=True)
nltk.download('punkt', quiet=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def preprocess_text(text):
    stemmer = PorterStemmer()
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = nltk.word_tokenize(text)
    stemmed = [stemmer.stem(token) for token in tokens]
    return ' '.join(stemmed)

def main():
    print("Initializing EnergyAI ML Pipeline...")
    
    # Step 1: Load training data
    data_path = os.path.join(BASE_DIR, 'training_data.json')
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    with open(data_path, 'r') as f:
        training_data = json.load(f)

    print(f"[OK] Loaded {len(training_data)} training examples")
    
    texts = [item['text'] for item in training_data]
    intents = [item['intent'] for item in training_data]
    
    # Encoding labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(intents)
    
    intent_classes = label_encoder.classes_
    print(f"[OK] Intent classes: {len(intent_classes)} ({', '.join(intent_classes)})")

    # Step 2: Preprocess
    print("Preprocessing text...")
    processed_texts = [preprocess_text(text) for text in texts]

    # Step 3: TF-IDF
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=3000, sublinear_tf=True)
    X = vectorizer.fit_transform(processed_texts)
    
    # Train / Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"[OK] Train/Test split: {X_train.shape[0]} / {X_test.shape[0]}")
    print(f"[OK] TF-IDF vocabulary: {len(vectorizer.vocabulary_)} terms")

    # Step 4: Random Forest
    print("[OK] Training RandomForest (200 trees)...")
    clf = RandomForestClassifier(n_estimators=200, max_depth=None, random_state=42, class_weight='balanced')
    clf.fit(X_train, y_train)
    print("[OK] Training complete.\n")

    # Step 5: Evaluate
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.inverse_transform(sorted(list(set(y_test))))))
    print(f"Overall Accuracy: {acc * 100:.1f}%\n")
    
    # Report saving for info page
    report_dict = classification_report(y_test, y_pred, target_names=label_encoder.inverse_transform(sorted(list(set(y_test)))), output_dict=True)
    report_dict['overall_accuracy'] = acc
    report_dict['total_examples'] = len(training_data)
    with open(os.path.join(BASE_DIR, 'training_report.json'), 'w') as f:
        json.dump(report_dict, f, indent=2)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=intent_classes, yticklabels=intent_classes)
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.title('Intent Classification Confusion Matrix')
    
    static_img_dir = os.path.join(os.path.dirname(BASE_DIR), 'static', 'img')
    os.makedirs(static_img_dir, exist_ok=True)
    confusion_path = os.path.join(static_img_dir, 'confusion_matrix.png')
    
    plt.savefig(confusion_path, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] Confusion matrix saved to {confusion_path}")

    # Also save to ml_models for Viva proof requirements
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=intent_classes, yticklabels=intent_classes)
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.title('Intent Classification Confusion Matrix')
    plt.savefig(os.path.join(BASE_DIR, 'confusion_matrix.png'), bbox_inches='tight')
    plt.close()

    # Step 6: Save Artifacts
    joblib.dump(vectorizer, os.path.join(BASE_DIR, 'tfidf_vectorizer.pkl'))
    joblib.dump(clf, os.path.join(BASE_DIR, 'intent_classifier.pkl'))
    joblib.dump(label_encoder, os.path.join(BASE_DIR, 'label_encoder.pkl'))
    
    print(f"[OK] Models saved to {BASE_DIR}")

if __name__ == '__main__':
    main()
