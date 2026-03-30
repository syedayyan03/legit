import sys
import os

# Add the project root to sys.path to import backend modules
sys.path.append(os.getcwd())

from backend.predictor import JobPredictor

def test_predictor():
    predictor = JobPredictor()
    
    test_samples = [
        {
            "title": "Earn $5000/week! Immediate hiring.",
            "description": "Basic knowledge in seek, no degree required. Flexible hours.",
            "company_profile": "Davidson, Jones and Gomez - Established 2003.",
            "requirements": "Basic knowledge in seek, no degree required.",
            "benefits": "Flexible hours.",
            "type": "Website"
        },
        {
            "title": "Senior Software Engineer",
            "description": "We are looking for a dedicated professional to join our team. requires 5 years of experience.",
            "company_profile": "Tech Solutions Inc. is a leader in the Technology industry.",
            "requirements": "Bachelor's degree in CS, 5+ years experience.",
            "benefits": "Health insurance, 401(k), flexible hours.",
            "type": "Website"
        }
    ]
    
    for i, sample in enumerate(test_samples):
        result = predictor.predict(sample)
        print(f"Sample {i+1}:")
        print(f"  Title: {sample['title']}")
        print(f"  Prediction: {result['prediction']}")
        print(f"  Confidence: {result['confidence']}%")
        print(f"  Risk Factors: {result['risk_factors']}")
        print("-" * 20)

if __name__ == "__main__":
    test_predictor()
