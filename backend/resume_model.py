import pandas as pd
import re
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

skills_db = [
"python","java","c","c++","javascript","html","css","sql",
"machine learning","deep learning","data analysis",
"react","node","django","flask","aws","docker",
"git","github","tensorflow","pandas","numpy",
"data structures","algorithms"
]

class ResumeAnalyzer:

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.model = LogisticRegression()

    def train(self, dataset_path):

        data = pd.read_csv(dataset_path)

        X = data["text"]
        y = data["label"]

        X_vec = self.vectorizer.fit_transform(X)

        self.model.fit(X_vec, y)

    def save_model(self):

        pickle.dump(self.model, open("backend/models/custom_resume_model.pkl","wb"))
        pickle.dump(self.vectorizer, open("backend/models/custom_vectorizer.pkl","wb"))

    def load_model(self):

        self.model = pickle.load(open("backend/models/custom_resume_model.pkl","rb"))
        self.vectorizer = pickle.load(open("backend/models/custom_vectorizer.pkl","rb"))

    def clean_text(self, text):

        text = text.lower()
        text = re.sub(r"[^a-zA-Z0-9 ]","",text)

        return text

    def extract_skills(self, text):

        text = text.lower()

        found = []

        for skill in skills_db:
            if skill in text:
                found.append(skill)

        return found

    def score_resume(self, text):
        try:
            cleaned_text = self.clean_text(text)
            vec = self.vectorizer.transform([cleaned_text])
            probability = self.model.predict_proba(vec)[0][1]
            score = int(probability * 100)
            return score
        except Exception as e:
            print(f"[RESUME_MODEL] EXCEPTION: {e}", flush=True)
            return 50 # Default fallback

    def analyze(self, text):

        score = self.score_resume(text)

        skills = self.extract_skills(text)

        missing = list(set(skills_db) - set(skills))

        tips = []

        if len(text.split()) < 150:
            tips.append("Resume content is too short")

        if "project" not in text.lower():
            tips.append("Add project section")

        if "experience" not in text.lower():
            tips.append("Add experience or internship")

        if "github" not in text.lower():
            tips.append("Add GitHub profile")

        return {
            "score": score,
            "skills_detected": skills,
            "missing_skills": missing[:10],
            "suggestions": tips
        }
