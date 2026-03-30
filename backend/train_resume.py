from resume_model import ResumeAnalyzer
import os

# Ensure models dir exists
os.makedirs("backend/models", exist_ok=True)

analyzer = ResumeAnalyzer()

analyzer.train("dataset/resume_dataset.csv")

analyzer.save_model()

print("Model trained and saved")
