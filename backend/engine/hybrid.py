from engine.rule_engine import evaluate_rules
from engine.ml_engine import predict_scam_probability

# Scoring Weights
RULE_WEIGHT = 0.4
ML_WEIGHT = 0.6

def compute_risk(message: str) -> dict:
    """Combines Rule Score and ML Probability into a Hybrid Score."""
    
    # Check length
    if len(message.strip().split()) < 3:
        return {
            "error": "Insufficient context for reliable analysis. Message too short."
        }
        
    # Get scores
    rule_results = evaluate_rules(message)
    ml_prob = predict_scam_probability(message)
    
    # Calculate Rule Score (normalized locally now)
    rule_score = rule_results["rule_score"]
    raw_trigger_weight = rule_results.get("triggered_weight", 0.0)
    
    # Tiered Calibrated Logic
    risk_level = "Low"
    rec = "Message appears safe, but always verify unknown senders or requests."
    decision_reason = "No significant risk signals detected."
    final_score = 0.0
    
    # Calibration adjustments based on False Positive testing:
    # ML model heavily flags all transactional SMS (OTP/Debits) ~98% due to dataset bias.
    # We must require at least some Rule corroboration to trigger a High ML Override.
    # We require raw_trigger_weight >= 0.20 (so a plain 0.15 Link doesn't trigger High if a friend sends it).
    if ml_prob >= 0.82 and raw_trigger_weight >= 0.20:
        risk_level = "High"
        final_score = max(ml_prob, rule_score)
        rec = "This message is likely fraudulent. Do NOT interact. Do not click links or share details."
        decision_reason = f"High Risk Override: Strong AI pattern corroborated by explicit rule triggers (Raw Wt: {raw_trigger_weight})."
    elif raw_trigger_weight >= 0.40:
        risk_level = "High"
        final_score = rule_score
        rec = "This message is likely fraudulent. Do NOT interact. Do not click links or share details."
        decision_reason = f"High Rule Override applied: Explicit mathematical fraud indicators found (Raw Wt: {raw_trigger_weight})."
    else:
        # Moderate Blend
        final_score = (0.5 * ml_prob) + (0.5 * rule_score)

        if final_score < 0.35:
            risk_level = "Low"
            rec = "Message appears safe, but always verify unknown senders or requests."
            decision_reason = "Hybrid calculation shows very low risk signals."
        elif final_score < 0.65:
            risk_level = "Medium"
            rec = "Exercise caution. Do not share sensitive information or click unknown links."
            decision_reason = "Hybrid calculation detects a moderate blend of suspicious signals."
        else:
            risk_level = "High"
            rec = "This message is likely fraudulent. Do NOT interact. Do not click links or share details."
            decision_reason = "Hybrid logic calculation crossed high threshold."
        
    # --- Terminal Logging ---
    print("\n" + "="*50)
    print(f"🕵️  FRAUD ANALYSIS REPORT")
    print("="*50)
    print(f"Message:      \"{message[:50]}{'...' if len(message) > 50 else ''}\"")
    print(f"Rule Score:   {rule_score:.2f} (Weight: {RULE_WEIGHT * 100}%)")
    print(f"AI Score:     {ml_prob:.4f} (Weight: {ML_WEIGHT * 100}%)")
    print("-" * 50)
    print(f"HYBRID SCORE: {final_score:.2f} / 1.00")
    print(f"RISK LEVEL:   [{risk_level.upper()}]")
    if rule_results["triggered_rules"]:
        print(f"Triggered:    {', '.join(rule_results['triggered_rules'])}")
    print("="*50 + "\n")

    # Construct final object
    return {
        "risk_level": risk_level,
        "final_score": round(final_score, 2),
        "rule_score": rule_score,
        "ml_probability": ml_prob,
        "triggered_rules": rule_results["triggered_rules"],
        "matched_phrases": rule_results["matched_phrases"],
        "explanations": rule_results["explanations"],
        "recommendation": rec,
        "decision_reason": decision_reason
    }
