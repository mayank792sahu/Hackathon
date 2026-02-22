import json
from backend.engine.hybrid import compute_risk
from backend.engine.ml_engine import load_models

TEST_CASES = [
    # --- OBVIOUS SCAMS (Should be HIGH risk) ---
    {
        "type": "Phishing Link + Impersonation",
        "message": "Dear SBI User, your account will be blocked today. Please update your PAN card immediately at http://sbi-update-kyc.xyz",
        "expected_risk": "High"
    },
    {
        "type": "Urgent OTP Request",
        "message": "Do not share this OTP with anyone. Your secret PIN to verify the transaction is 492011. Send it back to confirm.",
        "expected_risk": "High"
    },
    {
        "type": "Lottery/Reward Scam",
        "message": "Congratulations! You have won a cash prize of Rs 50,000 in the lucky draw. Contact us to claim your reward before the final chance expires.",
        "expected_risk": "High"
    },
    {
        "type": "Obfuscated URL",
        "message": "Your package from BlueDart is stuck at customs due to an unpaid fee. Please pay the fee to release it: bit.ly/3kX9z",
        "expected_risk": "High"
    },
    {
        "type": "Financial Information Phishing",
        "message": "Please verify your credit card ending in 4123 5512 8821 0012 to prevent suspension. Contact icici support.",
        "expected_risk": "High"
    },

    # --- FALSE POSITIVE TESTS (Should be LOW/MEDIUM risk - Legitimate messages with 'scary' keywords) ---
    {
        "type": "Legitimate Bank Alert (Transactional)",
        "message": "HDFC Bank: Rs. 500.00 debited from a/c **8210 on 22-Feb-26. Not you? Call 18002026161 to block card.",
        "expected_risk": "Low/Medium"
    },
    {
        "type": "Legitimate OTP Delivery",
        "message": "849201 is your OTP for transaction at Amazon. DO NOT share this with anyone. Bank will never call you for OTP.",
        "expected_risk": "Low/Medium"
    },
    {
        "type": "Legitimate Courier Update",
        "message": "Your BlueDart package AWB 182910291 is out for delivery. Track at https://bluedart.com/track",
        "expected_risk": "Low/Medium"
    },
    {
        "type": "Legitimate Work Message (Urgency)",
        "message": "Hey Rahul, can you urgently send me the presentation? We need it within 2 hours for the meeting.",
        "expected_risk": "Low"
    },
    {
        "type": "Legitimate Friend Message (Links/Finance)",
        "message": "Bro, I just paid for the movie tickets on Paytm. Send me your share. Here is the booking link: https://bookmyshow.com/xyz",
        "expected_risk": "Low"
    }
]

def run_tests():
    print("="*80)
    print("🔋  LOADING ML MODELS INTO MEMORY...")
    load_models()
    print("="*80)
    print("🚀  HYBRID ENGINE CALIBRATION & VERIFICATION SUITE")
    print("="*80)
    
    passed = 0
    total = len(TEST_CASES)
    
    output_data = []
    
    for idx, test in enumerate(TEST_CASES, 1):
        result = compute_risk(test['message'])
        actual_risk = result['risk_level']
        expected = test['expected_risk']
        
        # Validation Logic
        is_pass = False
        if expected == "Low/Medium" and actual_risk in ["Low", "Medium"]:
            is_pass = True
        elif expected == actual_risk:
            is_pass = True
            
        status = "PASS" if is_pass else "FAIL"
        if is_pass:
            passed += 1
            
        output_data.append({
            "test_name": test['type'],
            "message": test['message'],
            "expected_risk": expected,
            "actual_risk": actual_risk,
            "status": status,
            "rule_score": result['rule_score'],
            "ml_probability": result['ml_probability'],
            "final_score": result['final_score'],
            "decision_reason": result.get('decision_reason', 'N/A'),
            "triggered_rules": result['triggered_rules']
        })
    
    with open('test_output.json', 'w') as f:
        json.dump({"total": total, "passed": passed, "results": output_data}, f, indent=4)
    print(f"🏆  FINAL SCORE: {passed}/{total} TESTS PASSED. Results saved to test_output.json")

if __name__ == "__main__":
    run_tests()
