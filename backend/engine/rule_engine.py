import json
import os
import re

RULES_FILE = os.path.join(os.path.dirname(__file__), "../admin/rules.json")

def load_rules():
    """Loads active rules from JSON, falls back to empty if failure."""
    try:
        with open(RULES_FILE, "r") as f:
            all_rules = json.load(f)
            return [r for r in all_rules if r.get("enabled", True)]
    except Exception as e:
        print(f"Error loading rules: {e}")
        return []

def evaluate_rules(message: str) -> dict:
    """Evaluates message against all active rules."""
    rules = load_rules()
    msg_lower = message.lower()
    
    total_active_weight = 0.0
    triggered_weight = 0.0
    triggered = []
    matched_phrases = set()
    explanations = []

    for rule in rules:
        total_active_weight += rule["weight"]
        triggered_rule = False
        is_regex = rule.get("is_regex", False)
        
        for kw in rule["keywords"]:
            if is_regex:
                try:
                    match = re.search(kw, message, re.IGNORECASE)
                    if match:
                        matched_phrases.add(match.group(0))
                        triggered_rule = True
                except Exception as e:
                    print(f"Regex error on {kw}: {e}")
            else:
                # Simple keyword match mapping
                if kw.lower() in msg_lower:
                    matched_phrases.add(kw)
                    triggered_rule = True
                
        if triggered_rule:
            triggered_weight += rule["weight"]
            triggered.append(rule["category"])
            explanations.append(rule["explanation"])

    # Normalize score proportionally to avoid exploding weights
    if total_active_weight > 0:
        normalized_score = triggered_weight / total_active_weight
    else:
        normalized_score = 0.0
        
    # Cap score at 1.0 just in case
    normalized_score = min(normalized_score, 1.0)
    
    return {
        "rule_score": round(normalized_score, 2),
        "triggered_weight": round(triggered_weight, 2),
        "triggered_rules": triggered,
        "matched_phrases": list(matched_phrases),
        "explanations": explanations
    }
