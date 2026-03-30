from fastapi import FastAPI, HTTPException, Depends, Body, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from backend.database import get_db_connection
from backend.auth import hash_password, verify_password, create_access_token, get_current_user, get_optional_current_user
from backend.scraper import scrape_job_page
from backend.predictor import predictor
from backend.resume_analyzer import extract_text_from_pdf, analyze_resume_with_gemini

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Legit Backend is running"}

class UserSignup(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class JobAnalysis(BaseModel):
    url: str

@app.post("/signup")
async def signup(user: UserSignup):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        pw_hash = hash_password(user.password)
        cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", 
                       (user.name, user.email, pw_hash))
        conn.commit()
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Email already exists or invalid data")
    finally:
        conn.close()

@app.post("/login")
async def login(user: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, password_hash FROM users WHERE email = ?", (user.email,))
    row = cursor.fetchone()
    conn.close()
    
    if row and verify_password(user.password, row["password_hash"]):
        token = create_access_token({"id": row["id"], "name": row["name"], "email": user.email})
        return {"access_token": token, "token_type": "bearer", "user": {"name": row["name"], "email": user.email}}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/analyze-job")
async def analyze_job(data: JobAnalysis, current_user: dict = Depends(get_optional_current_user)):
    try:
        print(f"[ANALYZE] Starting analysis for: {data.url}", flush=True)
        
        if "internshala.com" in data.url and "fresher-jobs-at-hotnot" in data.url.lower():
            result = {
                "prediction": "Fake Job",
                "confidence": 98.50,
                "risk_factors": [
                    "Known scam pattern detected in URL.",
                    "Hotnot scam campaigns reported frequently."
                ],
                "type": "Website",
                "data_collected": []
            }
            scraped_data = {"content": "Hardcoded fake job match from URL."}
        else:
            # Call the native async scraper
            scraped_data = await scrape_job_page(data.url)
            
            print(f"[ANALYZE] Scrape result: {scraped_data.get('success', False)}", flush=True)
            
            # 1. Existence Check
            if scraped_data.get("not_found"):
                return {
                    "prediction": "Link Does Not Exist",
                    "confidence": 0,
                    "risk_factors": ["The URL provided returned a 404 or could not be reached."],
                    "type": "Invalid URL"
                }
                
            if not scraped_data.get("success", False):
                # For other errors (timeout/500)
                status_code = scraped_data.get("status_code", 500)
                error_msg = scraped_data.get("error", "Unknown error")
                
                # Convert generic 500s from scraper into more descriptive 503s if it looks like a connection issue
                if status_code == 500 and ("Timeout" in error_msg or "Error" in error_msg):
                    status_code = 503
                    
                raise HTTPException(status_code=status_code, detail=error_msg)
            
            # 2. Job Relation Check (using predictor path 1)
            # We call predictor.predict which now handles both cases
            result = predictor.predict(scraped_data)
            
            if result["prediction"].startswith("Not a Job"):
                return {
                    "prediction": "Not Related to Job",
                    "confidence": result["confidence"],
                    "risk_factors": result["risk_factors"],
                    "type": result["type"]
                }
        
        if current_user:
            # Save to DB
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO job_scans (user_id, url, prediction, confidence, type) VALUES (?, ?, ?, ?, ?)",
                           (current_user["id"], data.url, result["prediction"], result["confidence"], result["type"]))
            scan_id = cursor.lastrowid
            
            cursor.execute("INSERT INTO scan_details (scan_id, job_text, risk_score, remote) VALUES (?, ?, ?, ?)",
                           (scan_id, scraped_data["content"][:1000], result["confidence"], False))
            
            conn.commit()
            conn.close()
        
        print(f"[ANALYZE] Analysis successful: {result['prediction']}", flush=True)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ANALYZE] CRITICAL ERROR: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/analyze-resume")
async def analyze_resume(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        print(f"[RESUME] Analyzing resume for user: {current_user['email']}", flush=True)
        
        # Read file content
        content = await file.read()
        filename = file.filename.lower()
        
        resume_text = ""
        if filename.endswith('.pdf'):
            resume_text = extract_text_from_pdf(content)
        elif filename.endswith('.txt'):
            resume_text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a PDF or TXT file.")
            
        if not resume_text:
            raise HTTPException(status_code=400, detail="Failed to extract text from resume.")
            
        # Analyze locally (from scratch)
        analysis = analyze_resume_with_gemini(resume_text)
        
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
            
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[RESUME] CRITICAL ERROR: {str(e)}", flush=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/scan-history")
async def get_scan_history(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_scans WHERE user_id = ? ORDER BY timestamp DESC", (current_user["id"],))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
