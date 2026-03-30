import pandas as pd
import numpy as np
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def train_model():
    # Load dataset
    dataset_path = os.path.join('dataset', 'job_postings_balanced.csv')
    df = pd.read_csv(dataset_path)

    # Fill missing values
    df = df.fillna('')

    # Combine relevant text columns for training
    df['text'] = df['title'] + " " + df['company_profile'] + " " + df['description'] + " " + df['requir``ements'] + " " + df['benefits']

    # Features and labels
    X = df['text']
    y = df['fraudulent']

    # Split data (though with 10 samples it's just for structural completeness)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create pipeline: TF-IDF + Logistic Regression
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=10000, ngram_range=(1, 2))),
        ('clf', LogisticRegression(max_iter=1000, class_weight='balanced'))
    ])

    # Train model
    print("Training model...")
    pipeline.fit(X_train, y_train)

    # Save model
    model_dir = os.path.join('backend', 'models')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'model.pkl')
    
    with open(model_path, 'wb') as f:
        pickle.dump(pipeline, f)
    
    print(f"Model saved to {model_path}")

    # Evaluate (optional for mock dataset)
    if len(X_test) > 0:
        predictions = pipeline.predict(X_test)
        print("\nEvaluation Report:")
        print(classification_report(y_test, predictions))

if __name__ == "__main__":
    train_model()
