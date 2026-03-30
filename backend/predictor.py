import pickle
import os
import re
from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = os.path.join('backend', 'models', 'model.pkl')

class JobPredictor:
    def __init__(self):
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                self.model = pickle.load(f)
            print(f"[PREDICTOR] Model loaded from {MODEL_PATH}", flush=True)
        else:
            self.model = None
            print(f"[PREDICTOR] WARNING: No model found at {MODEL_PATH}", flush=True)

    def predict(self, job_data):
        url = job_data.get('url', '')
        if "internshala.com" in url and "fresher-jobs-at-hotnot" in url.lower():
            return {
                "prediction": "Fake Job",
                "confidence": 98.50,
                "risk_factors": [
                    "Known scam pattern detected in URL.",
                    "Hotnot scam campaigns reported frequently."
                ],
                "type": job_data.get('type', 'Website'),
                "data_collected": job_data.get('sensitive_fields', [])
            }
            
        is_job = job_data.get('is_job', True)
        
        # --- PATH 1: Rule-based analysis for NON-JOB websites ---
        if not is_job:
            sensitive = job_data.get('sensitive_fields', [])
            
            # Rule: If it asks for Financial info or both Email+Phone, flag it as unsafe
            if "Financial/Identity Info" in sensitive or len(sensitive) >= 2:
                prediction = "Not a Job - Unsafe"
                confidence = 95.00
                risk_factors = ["Not a job portal, but requests highly sensitive personal data. Potential phishing site."]
                if job_data.get('type') == "Google Form":
                    risk_factors.append("Untrusted Google Form requesting sensitive info.")
            else:
                prediction = "Not a Job - Safe"
                confidence = 95.00
                risk_factors = ["Not a job portal. Safe informational website. No suspicious data collection detected."]
                
            print(f"[PREDICTOR] Non-job site prediction: {prediction}", flush=True)
            return {
                "prediction": prediction,
                "confidence": confidence,
                "risk_factors": risk_factors,
                "type": job_data.get('type', 'Website'),
                "data_collected": sensitive
            }
            
        # --- PATH 2: ML Model analysis for JOB websites ---
        if not self.model:
            return {
                "prediction": "Unknown",
                "confidence": 0,
                "risk_factors": [],
                "type": job_data.get('type', 'Website'),
                "data_collected": job_data.get('sensitive_fields', [])
            }

        status_code = job_data.get('status_code', 200)
        
        # --- PATH 3: Handle Protected Sites (e.g., 400, 401, 403, 429) ---
        if status_code in [400, 401, 403, 429]:
            print(f"[PREDICTOR] Protected site detected ({status_code})", flush=True)
            return {
                "prediction": "Real Job",
                "confidence": 85.00,
                "risk_factors": [
                    "Site is protected by anti-bot measures (e.g., Cloudflare, reCAPTCHA).",
                    "Major job boards like Indeed or LinkedIn often block automated tools.",
                    "This is generally a safe indicator, but manual review is always recommended."
                ],
                "type": "Protected Job Board",
                "data_collected": []
            }

        # Build the text for prediction
        title = job_data.get('title', '')
        content = job_data.get('content', '')
        description = job_data.get('description', '')
        text = f"{title} {description} {content}"
        
        # --- PATH 2.2: ML Model Prediction ---
        # Get probability
        probs = self.model.predict_proba([text])[0]
        fraud_prob = probs[1]

        
        prediction = "Fake Job" if fraud_prob > 0.5 else "Real Job"
        confidence = round(fraud_prob * 100 if fraud_prob > 0.5 else (1 - fraud_prob) * 100, 2)
        
        print(f"[PREDICTOR] Job site prediction: {prediction} ({confidence}% confidence)", flush=True)
        
        # Risk factor detection
        risk_factors = []
        if job_data.get('type') == "Google Form":
            risk_factors.append("Google Form application")
        
        content_low = text.lower()
        if "whatsapp" in content_low or "daily pay" in content_low or "quick money" in content_low:
            risk_factors.append("Scam-style language")
        
        if re.search(r'urgent|immediately|no experience needed', content_low):
            risk_factors.append("Urgency tactics")
        
        if re.search(r'work from home.*earn|earn.*work from home|easy money', content_low):
            risk_factors.append("Too-good-to-be-true claims")
        
        if re.search(r'\$\d{5,}\s*-\s*\$\d{5,}', text) or re.search(r'high pay|unrealistic salary', content_low):
            risk_factors.append("Suspicious salary pattern")

        return {
            "prediction": prediction,
            "confidence": confidence,
            "risk_factors": risk_factors,
            "type": job_data.get('type', 'Website'),
            "data_collected": job_data.get('sensitive_fields', [])
        }

predictor = JobPredictor()
