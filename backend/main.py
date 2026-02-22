from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import time

from engine.hybrid import compute_risk
from engine.ml_engine import load_models
from database.db import save_feedback, log_analysis, get_recent_logs

# Init FastAPI
app = FastAPI(title="Fraud Detection API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for MVP hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RULES_FILE = os.path.join(os.path.dirname(__file__), "admin/rules.json")

# Data Models
class MessageRequest(BaseModel):
    message: str

class FeedbackRequest(BaseModel):
    message: str
    predicted_risk: str
    user_correction: str

class RuleUpdate(BaseModel):
    category: str
    weight: float
    keywords: list[str]
    explanation: str
    is_regex: bool = False

# Startup Event: Load ML Model into memory
@app.on_event("startup")
def startup_event():
    load_models()

# --- Core Analysis Endpoint ---

@app.post("/analyze")
def analyze_message(req: MessageRequest, background_tasks: BackgroundTasks):
    start_time = time.time()
    if not req.message or len(req.message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    result = compute_risk(req.message)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    end_time = time.time()
    processing_time = round(end_time - start_time, 3)
    result["processing_time_sec"] = processing_time
    
    # Run the database logging in the background so it doesn't delay the API response
    background_tasks.add_task(
        log_analysis,
        message=req.message,
        risk_level=result["risk_level"],
        final_score=result["final_score"],
        ml_prob=result["ml_probability"],
        rule_score=result["rule_score"],
        processing_time=processing_time
    )
        
    return result

# --- Admin API Endpoints ---

@app.get("/admin/logs")
def get_logs(limit: int = 100):
    """Retrieve the most recent analysis logs."""
    return get_recent_logs(limit)

@app.get("/admin/rules")
def get_rules():
    """Retrieve all configurable rules from JSON."""
    if not os.path.exists(RULES_FILE):
        return []
    with open(RULES_FILE, "r") as f:
        return json.load(f)

@app.post("/admin/rules")
def add_rule(new_rule: RuleUpdate):
    """Add a new rule to JSON configuration."""
    rules = get_rules()
    
    # Assign new incremented ID
    new_id = max([r.get("id", 0) for r in rules] + [0]) + 1
    rule_obj = {
        "id": new_id,
        "category": new_rule.category,
        "weight": new_rule.weight,
        "keywords": new_rule.keywords,
        "explanation": new_rule.explanation,
        "enabled": True,
        "is_regex": new_rule.is_regex
    }
    
    rules.append(rule_obj)
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=2)
        
    return {"status": "success", "rule": rule_obj}

@app.put("/admin/rules/{rule_id}")
def toggle_rule(rule_id: int):
    """Toggle a rule on/off (enabled/disabled)."""
    rules = get_rules()
    for r in rules:
        if r["id"] == rule_id:
            r["enabled"] = not r.get("enabled", True)
            with open(RULES_FILE, "w") as f:
                json.dump(rules, f, indent=2)
            return {"status": "success", "message": "Rule toggled", "enabled": r["enabled"]}
            
    raise HTTPException(status_code=404, detail="Rule not found")

@app.delete("/admin/rules/{rule_id}")
def delete_rule(rule_id: int):
    """Delete a rule by ID."""
    rules = get_rules()
    filtered = [r for r in rules if r["id"] != rule_id]
    
    if len(filtered) == len(rules):
        raise HTTPException(status_code=404, detail="Rule not found")
        
    with open(RULES_FILE, "w") as f:
        json.dump(filtered, f, indent=2)
        
    return {"status": "success", "message": "Rule deleted"}

# --- Database Storage Endpoint (Optional Scope) ---
@app.post("/feedback")
def log_feedback(req: FeedbackRequest):
    """Logs an analysis correction from the user into SQLite for dynamic ML retraining."""
    save_feedback(req.message, req.predicted_risk, req.user_correction)
    return {"status": "success", "message": "Feedback saved for next model retrain."}

@app.post("/admin/retrain")
def trigger_retrain():
    """Triggers the Python script to retrain the ML model including the new dynamic feedback data."""
    import subprocess
    import os
    
    script_path = os.path.join(os.path.dirname(__file__), "train_model.py")
    try:
        # Run the training script headlessly
        subprocess.run(["python", script_path], check=True)
        # Reload models into memory safely after completion
        load_models()
        return {"status": "success", "message": "Model retrained aggressively and loaded into memory."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
