import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "fraud_knowledge.db")

def init_db():
    """Initializes the SQLite database and feedback table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table to store dynamic ML retraining metadata
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            predicted_risk TEXT NOT NULL,
            user_correction TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table to store historical logs of all analyzed messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyzed_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            final_score REAL NOT NULL,
            ml_probability REAL,
            rule_score REAL,
            processing_time_sec REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_feedback(message: str, predicted_risk: str, user_correction: str):
    """Saves user feedback on an analyzed message."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO feedback (message, predicted_risk, user_correction) VALUES (?, ?, ?)",
        (message, predicted_risk, user_correction)
    )
    conn.commit()
    conn.close()

def get_all_feedback():
    """Retrieves all feedback rows to be appended to training data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT message, user_correction FROM feedback")
    rows = cursor.fetchall()
    conn.close()
    return rows

def log_analysis(message: str, risk_level: str, final_score: float, ml_prob: float, rule_score: float, processing_time: float):
    """Saves a log of a standard analysis calculation into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO analyzed_logs 
        (message, risk_level, final_score, ml_probability, rule_score, processing_time_sec) 
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (message, risk_level, final_score, ml_prob, rule_score, processing_time)
    )
    conn.commit()
    conn.close()

def get_recent_logs(limit: int = 100):
    """Retrieves the most recent analyzed messages metadata."""
    conn = sqlite3.connect(DB_PATH)
    # Output rows as dicts for FastAPI JSON serialization
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, message, risk_level, final_score, ml_probability, rule_score, processing_time_sec, timestamp 
        FROM analyzed_logs 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Run initialization on import
init_db()
