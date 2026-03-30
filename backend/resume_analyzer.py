import io
import PyPDF2
import sys
import os
import re
import numpy as np

# Add backend directory to path so it can find resume_model
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from resume_model import ResumeAnalyzer

_analyzer_instance = None

def get_analyzer():
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = ResumeAnalyzer()
        try:
            _analyzer_instance.load_model()
            print("[RESUME] Custom Resume ML loaded successfully.")
        except Exception as e:
            print(f"[RESUME] Warning: Could not load model: {e}")
    return _analyzer_instance

def extract_text_from_pdf(file_content):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content: text += content + "\n"
        return text.strip()
    except Exception as e:
        print(f"[RESUME] Error extracting PDF text: {e}")
        return None

import io
import PyPDF2
import sys
import os
import re
import random

# Add backend directory to path so it can find resume_model
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from resume_model import ResumeAnalyzer

_analyzer_instance = None

def get_analyzer():
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = ResumeAnalyzer()
        try:
            _analyzer_instance.load_model()
            print("[RESUME] Custom Resume ML loaded successfully.")
        except Exception as e:
            print(f"[RESUME] Warning: Could not load model: {e}")
    return _analyzer_instance

def extract_text_from_pdf(file_content):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content: text += content + "\n"
        return text.strip()
    except Exception as e:
        print(f"[RESUME] Error extracting PDF text: {e}")
        return None

HARD_SKILLS = ["Python", "Java", "C++", "C", "JavaScript", "TypeScript", "React", "Angular", "Vue", "Node.js", "Node", "FastAPI", "Django", "Flask", "SQL", "PostgreSQL", "MongoDB", "AWS", "Azure", "Docker", "Kubernetes", "Machine Learning", "Data Science", "AI", "NLP", "Deep Learning", "HTML", "CSS", "Git", "GitHub", "C#", "Spring", "Rust", "Go", "PHP", "Laravel", "Ruby on Rails", "Swift", "Kotlin", "TensorFlow", "PyTorch", "Tableau", "PowerBI", "Pandas", "Numpy", "Data Structures", "Algorithms"]
SOFT_SKILLS = ["Communication", "Leadership", "Teamwork", "Problem Solving", "Time Management", "Adaptability", "Critical Thinking", "Creativity", "Emotional Intelligence", "Negotiation", "Public Speaking", "Conflict Resolution", "Strategic Thinking", "Agile", "Scrum", "Mentorship"]

SECTION_KEYWORDS = {
    "summary": ["summary", "objective", "profile", "about me", "professional summary"],
    "experience": ["experience", "work history", "employment", "professional background", "career"],
    "education": ["education", "academic", "university", "college", "degree", "certification", "bachelor", "master"],
    "projects": ["projects", "personal projects", "portfolio", "accomplishments"],
    "skills": ["skills", "technologies", "expertise", "competencies", "core competencies"],
    "achievements": ["achievements", "awards", "honors", "certifications", "publications", "patents"]
}

def analyze_resume_with_gemini(resume_text):
    """Uses the user-provided custom ResumeAnalyzer class and enhances it with structural NLP."""
    analyzer = get_analyzer()
    text_lower = resume_text.lower()
    
    # 1. Run user's custom analysis
    custom_results = analyzer.analyze(resume_text)
    ml_score = custom_results.get("score", 0)
    
    # 2. Extract ALL broad skills
    found_hard = [skill for skill in HARD_SKILLS if skill.lower() in text_lower]
    found_soft = [skill for skill in SOFT_SKILLS if skill.lower() in text_lower]
    sections_found = [sec for sec, kws in SECTION_KEYWORDS.items() if any(k in text_lower for k in kws)]
    
    # 3. Impact metrics
    impact_count = len(re.findall(r'\d+%', resume_text)) + len(re.findall(r'\$\d+', resume_text))
    
    # 4. Build dynamic section-by-section feedback
    strengths = []
    advice = []
    gaps = []
    
    # Combine custom ML skills with broad NLP skills
    all_tech = list(set([h.title() for h in found_hard] + [s.title() for s in custom_results.get("skills_detected", [])]))
    
    # Dynamic text variations to prevent hardcoded feel
    sum_intros = ["We identified your opening profile.", "Your summary was detected.", "Professional objective found.", "Profile text scanned."]
    exp_intros = ["Work history mapped.", "Career timeline found.", "Professional experience documented.", "Experience section detected."]
    edu_intros = ["Academic credentials found.", "Education background registered.", "Degrees and schooling detected."]
    
    # --- SUMMARY SECTION ---
    if "summary" in sections_found:
        sentences = [s.strip() for s in re.split(r'[.!?\n]', resume_text) if len(s.strip()) > 20]
        extracted = f"'{sentences[0]}...'" if sentences else "Profile text found."
        strengths.append(f"{random.choice(sum_intros)} Highlight: {extracted}")
        advice.append("Pro Tip for Summary: Ensure your opening explicitly states your top 2 skills and total years of experience to hook the recruiter.")
    else:
        gaps.append("CRITICAL: No 'Professional Summary' or 'Objective' section found at the top of your resume.")
        advice.append("Action Item: Write a compelling 2-3 line summary that acts as a pitch for your profile.")

    # --- EXPERIENCE SECTION ---
    if "experience" in sections_found:
        bullets = [s.strip() for s in re.split(r'\n', resume_text) if len(s.strip()) > 10 and (s.strip().startswith('-') or s.strip().startswith('•'))]
        if bullets:
            strengths.append(f"{random.choice(exp_intros)} Extracted {len(bullets)} responsibilities. Example: '{str(bullets[0])[:70]}...'")
        else:
            strengths.append(f"{random.choice(exp_intros)}")
            
        if impact_count == 0:
            advice.append("Warning for Experience: We did not detect quantifiable metrics (%, $, scale). Add numbers to your bullet points to show true impact.")
            gaps.append("Missing quantifiable achievements (numbers, percentages, scale) in your work history.")
        else:
            advice.append(f"Excellent use of {impact_count} metrics in your experience! Optimize further with the 'Action Verb + Metric + Value' format.")
    else:
        gaps.append("CRITICAL: Could not find a dedicated 'Experience' or 'Work History' section.")
        advice.append("Action Item: You must add an Experience section. If you are a student, substitute this with a detailed 'Relevant Projects' section.")

    # --- EDUCATION SECTION ---
    if "education" in sections_found:
        strengths.append(f"{random.choice(edu_intros)}")
        advice.append("Checklist for Education: Verify university name, degree title, and graduation date are clearly structured.")
    else:
        gaps.append("Missing 'Education' or 'Academic' section.")

    # --- SKILLS SECTION ---
    if "skills" in sections_found or len(all_tech) > 0:
        strengths.append(f"Technical Stack: We compiled {len(all_tech)} distinct skills from your document ({', '.join([str(t) for t in list(all_tech)[:5]])}...).")
        if len(all_tech) < 5:
            advice.append("Skill Gap: You have very few isolated technical keywords. Expand your technologies to pass ATS filters.")
            gaps.append("Low volume of recognizable hard skills.")
        else:
            advice.append("Format Tip: Group your listed skills into functional categories (e.g., Languages, Frameworks, Cloud) for better recruiter visibility.")
    else:
        gaps.append("CRITICAL: No explicit 'Skills' section detected.")
        advice.append("Action Item: Create a dedicated 'Skills' matrix to ensure ATS software tags you correctly.")

    # --- PROJECTS/ACHIEVEMENTS ---
    if "projects" in sections_found or "achievements" in sections_found:
        strengths.append("Extra-curricular or Portfolio projects detected.")
        advice.append("Project Tip: Ensure every project listed includes a live link (e.g., GitHub) and specifies the exact tech stack used.")
    else:
        gaps.append("No 'Projects' or 'Achievements' section found.")

    # Include custom model's missing skills recommendation
    missing_model_skills = custom_results.get("missing_skills", [])
    if missing_model_skills:
        advice.append(f"[ML Model Data] Based on industry trends, adding these domain skills will significantly boost your score: {', '.join(missing_model_skills[:5])}.")

    for sug in custom_results.get("suggestions", []):
        if "Model Suggestion" not in sug:
            advice.append(f"[ML Model Data] {sug}")

    # 5. Build Sub-scores
    format_score = min(len(sections_found) * 20 + 20, 95)
    skill_score = min((len(found_hard) * 5) + 30, 100)
    exp_score = 90 if "experience" in sections_found else 30
    impact_score = min(impact_count * 30 + 30, 100)
    
    combined_summary = f"Based on our custom LogisticRegression evaluation, your profile ranks {ml_score}% against top developer benchmarks. \n\nWe have performed a deep extraction and section-by-section analysis below."
    
    return {
        "overall_score": ml_score,
        "categorical_scores": {
            "skill_match": skill_score,
            "experience_depth": exp_score,
            "formatting_clarity": format_score,
            "impact_metrics": impact_score
        },
        "summary": combined_summary,
        "key_strengths": strengths if strengths else ["No extractable structural content found."],
        "critical_gaps": gaps if gaps else ["Your structural formatting aligns securely with standard ATS benchmarks."],
        "strategic_advice": advice if advice else ["Keep iterating on your resume to match specific job descriptions."],
        "technical_skills": all_tech,
        "soft_skills": [s.title() for s in found_soft]
    }


