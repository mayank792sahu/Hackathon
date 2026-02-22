import pickle
import os
from sentence_transformers import SentenceTransformer

MODEL_DIR = os.path.join(os.path.dirname(__file__), "../model")
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "classifier.pkl")

# Global instances (Loaded on startup)
transformer_instance = None
classifier_instance = None

def load_models():
    """Loads SentenceTransformer and logistic regression model from disk/hub."""
    global transformer_instance, classifier_instance
    try:
        print("Initializing NLP Transformer Model...")
        transformer_instance = SentenceTransformer('all-MiniLM-L6-v2')
            
        with open(CLASSIFIER_PATH, "rb") as f:
            classifier_instance = pickle.load(f)
            
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Error loading ML models: {e}")

def predict_scam_probability(message: str) -> float:
    """Predicts probability (0 to 1) of message being a scam."""
    if not transformer_instance or not classifier_instance:
        print("Warning: Models not loaded. Returning 0.0")
        return 0.0
        
    try:
        # Generate dense contextual embedding using transformer
        X = transformer_instance.encode([message])
        
        # predict_proba returns [[prob_class_0, prob_class_1]]
        # We want the probability of class 1 (Scam)
        prob = classifier_instance.predict_proba(X)[0][1]
        
        return round(float(prob), 4)
    except Exception as e:
        print(f"Prediction error: {e}")
        return 0.0
