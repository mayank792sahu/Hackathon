import json
from backend.engine.hybrid import compute_risk
from backend.engine.ml_engine import load_models

TEST_CASES = [
    # --- 10 SCAMS: PHISHING LINKS ---
    {"type": "Phishing", "message": "Dear SBI User, your account will be blocked today. Please update your PAN card immediately at http://sbi-update-kyc.xyz", "expected_risk": "High"},
    {"type": "Phishing", "message": "Income Tax Refund of Rs 15,490 has been approved. Click to claim your refund directly to bank: https://incometax-gov-in.club/refund", "expected_risk": "High"},
    {"type": "Phishing", "message": "Your Jio number KYC is expiring in 24 hrs. Click here to verify your Aadhaar to avoid suspension: bit.ly/jio-kyc-update", "expected_risk": "High"},
    {"type": "Phishing", "message": "Dear customer, your credit card 4123 **** 8821 will be charged Rs 9,999 for Amazon Prime. If not you, cancel it here: http://amazon-cancel-subs.top", "expected_risk": "High"},
    {"type": "Phishing", "message": "Your HDFC netbanking access is locked due to security reasons. Unlock now by entering your details at https://hdfc-secure.site", "expected_risk": "High"},
    {"type": "Phishing", "message": "India Post: Your package is stuck at the local sorting facility due to unpaid customs fee of Rs 49. Pay online: cutt.ly/indiapost", "expected_risk": "High"},
    {"type": "Phishing", "message": "Congratulations you have won iPhone 15 in the lucky draw! Claim your prize at http://free-prize-winner.online today.", "expected_risk": "High"},
    {"type": "Phishing", "message": "UIDAI alert: Your Aadhaar linked bank accounts will be frozen by RBI. Verify identity at https://uidai-auth.cc", "expected_risk": "High"},
    {"type": "Phishing", "message": "You've been selected for a remote WFH job earning Rs 5000/day. Contact HR now on whatsapp. Visit link: t.me/hr-jobs", "expected_risk": "High"},
    {"type": "Phishing", "message": "Your electricity power will be disconnected tonight at 9:30 PM because your previous month bill was not updated. Call electricity officer at 9876543210 or visit bit.ly/pay-bill", "expected_risk": "High"},

    # --- 10 SCAMS: URGENT / OTP ---
    {"type": "OTP Scam", "message": "Do not share this OTP with anyone. Your secret PIN to verify the transaction is 492011. Send it back to confirm.", "expected_risk": "High"},
    {"type": "OTP Scam", "message": "To stop the Rs 50,000 deduction from your HDFC account, please provide the 6-digit verification code you just received.", "expected_risk": "High"},
    {"type": "Impersonation", "message": "Hello this is Police Cyber Cell. We found illegal activity on your PAN card. Send us your Aadhaar number immediately or face arrest warrant.", "expected_risk": "High"},
    {"type": "Urgency", "message": "FINAL NOTICE: You must act immediately to stop legal action against you. Your loan EMI is overdue. Pay within 2 hours.", "expected_risk": "High"},
    {"type": "Reward", "message": "BIG CASH PRIZE! You are the lucky lottery winner of Rs 1,000,000. Send your bank details and PAN card to receive funds.", "expected_risk": "High"},
    {"type": "Urgency", "message": "Dear customer, last chance to redeem your 50,000 credit card reward points before they expire today. Log in now.", "expected_risk": "High"},
    {"type": "Impersonation", "message": "SBI alerting you: We observed suspicious login attempt. Forward the OTP received on SMS to block the fraudulent transaction.", "expected_risk": "High"},
    {"type": "OTP Scam", "message": "Dear user, the delivery executive is waiting outside. Please share the PIN 8912 to receive your courier.", "expected_risk": "High"},
    {"type": "Urgency", "message": "Your Whatsapp account will be deactivated in 30 minutes! Verify your phone number by sending the code via SMS.", "expected_risk": "High"},
    {"type": "Finance Phish", "message": "We need to verify your payment. Send us your UPI pin or credit card number and CVV to process the refund.", "expected_risk": "High"},

    # --- 10 LEGITIMATE: BANKING & OTP (False Positive Risk) ---
    {"type": "Legit Bank", "message": "HDFC Bank: Rs. 500.00 debited from a/c **8210 on 22-Feb-26. Not you? Call 18002026161 to block card.", "expected_risk": "Low/Medium"},
    {"type": "Legit Bank", "message": "Dear Customer, your A/c **4129 is credited with Rs 40,000.00 on 22-Feb-26 by NEFT. Avl Bal: Rs 55,200.00. SBI", "expected_risk": "Low/Medium"},
    {"type": "Legit OTP", "message": "849201 is your OTP for transaction at Amazon. DO NOT share this with anyone. Bank will never call you for OTP.", "expected_risk": "Low/Medium"},
    {"type": "Legit OTP", "message": "Use 123456 as your Swiggy login OTP. This is valid for 5 minutes. Never share it with anyone.", "expected_risk": "Low/Medium"},
    {"type": "Legit Finance", "message": "Your statement for ICICI Bank Credit Card ending 9012 for Jan 2026 is generated. Minimum Due: Rs 1500. Payment due by 15-Feb.", "expected_risk": "Low/Medium"},
    {"type": "Legit Bank", "message": "Alert: Login to your Axis Bank Internet Banking from IP 192.168.1.5 occurred. If this wasn't you, call customer care.", "expected_risk": "Low/Medium"},
    {"type": "Legit Finance", "message": "SIP of Rs. 5000 in Mutual Fund successfully processed on 01-Feb-26. Folio No 918291. - Groww.", "expected_risk": "Low/Medium"},
    {"type": "Legit OTP", "message": "Your Google verification code is 881290. Do not share this code with anyone.", "expected_risk": "Low/Medium"},
    {"type": "Legit Bank", "message": "Reminder: Your EMI of Rs 15,200 for Auto Loan is due on 05-Mar-26. Please maintain sufficient balance. - PNB", "expected_risk": "Low/Medium"},
    {"type": "Legit Transaction", "message": "Paid Rs. 150 to Zomato India via UPI. Txn Ref: 412910291029. - PhonePe", "expected_risk": "Low/Medium"},

    # --- 10 LEGITIMATE: PERSONAL & EVERYDAY ---
    {"type": "Personal", "message": "Hey Rahul! What time are we meeting for dinner tonight? Let me know.", "expected_risk": "Low"},
    {"type": "Personal", "message": "Mom said we are out of milk. Can you pick some up on your way home?", "expected_risk": "Low"},
    {"type": "Personal", "message": "Bro, I just paid for the movie tickets on Paytm. Send me your share. Here is the booking link: https://bookmyshow.com/xyz", "expected_risk": "Low/Medium"},
    {"type": "Personal", "message": "Did you finish the assignment yet? The deadline is midnight and I haven't started!", "expected_risk": "Low"},
    {"type": "Personal", "message": "Haha that meme you sent was hilarious! Good luck with your exam tomorrow.", "expected_risk": "Low"},
    {"type": "Personal", "message": "I'm stuck in traffic, might be 15 minutes late. Go ahead and order without me.", "expected_risk": "Low"},
    {"type": "Personal", "message": "Happy Birthday Anjali! Hope you have an amazing day and a great year ahead. Miss you!", "expected_risk": "Low"},
    {"type": "Personal", "message": "Can someone share the Wifi password for the conference room?", "expected_risk": "Low"},
    {"type": "Personal", "message": "I transferred the rent to your account. Let me know once you receive it. Thanks.", "expected_risk": "Low"},
    {"type": "Personal", "message": "Are we still playing football this weekend? We need two more players.", "expected_risk": "Low"},

    # --- 10 LEGITIMATE: WORK / DELIVERY / PROMOTIONS ---
    {"type": "Work Urgency", "message": "Hey team, the production server is down! We need to fix this urgently. Jump on the Zoom call now: https://zoom.us/j/123", "expected_risk": "Low/Medium"},
    {"type": "Work", "message": "Please review the attached quarterly report and send me your feedback by EOD. - Sarah", "expected_risk": "Low"},
    {"type": "Delivery", "message": "Your BlueDart package AWB 182910291 is out for delivery. Track at https://bluedart.com/track", "expected_risk": "Low/Medium"},
    {"type": "Delivery", "message": "Swiggy Genie: Your package has been picked up. Track your rider here: swiggy.in/track", "expected_risk": "Low/Medium"},
    {"type": "Promo", "message": "Up to 50% OFF on winter wear at Myntra! Sale ends tonight. Shop now: myntra.com/sale", "expected_risk": "Medium"},
    {"type": "Promo", "message": "Hungry? Grab 2 pizzas for the price of 1 at Domino's! Use code BOGO. Order at dominos.co.in", "expected_risk": "Low/Medium"},
    {"type": "Work Urgency", "message": "Can you urgently send me the presentation? We need it within 2 hours for the client meeting.", "expected_risk": "Low/Medium"},
    {"type": "Delivery", "message": "OTP for your Amazon delivery is 5192. Share with the agent only after receiving the package.", "expected_risk": "Low/Medium"},
    {"type": "Work", "message": "Don't forget to submit your timesheets for this week before 5 PM on Friday.", "expected_risk": "Low"},
    {"type": "Promo", "message": "Jio: Recharge with Rs. 299 to enjoy unlimited calls and 2GB/day data. Recharge now via MyJio app.", "expected_risk": "Low/Medium"}
]

def run_tests():
    print("="*80)
    print("🔋  LOADING ML MODELS INTO MEMORY...")
    load_models()
    print("="*80)
    print("🚀  50-ITEM LARGE-SCALE VERIFICATION & OVERFITTING SUITE")
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
            "rule_score": result.get('rule_score', 0),
            "ml_probability": result.get('ml_probability', 0),
            "final_score": result.get('final_score', 0),
            "decision_reason": result.get('decision_reason', 'N/A'),
            "triggered_rules": result.get('triggered_rules', [])
        })
        
        print(f"[{idx:02d}/50] {status} - Expected: {expected:10s} | Got: {actual_risk:10s} | ML: {result.get('ml_probability',0):.2f} | Rule: {result.get('rule_score',0):.2f}")
    
    with open('test_output_large.json', 'w') as f:
        json.dump({"total": total, "passed": passed, "results": output_data}, f, indent=4)
        
    print("\n" + "="*80)
    print(f"🏆  FINAL SCORE: {passed}/{total} TESTS PASSED. Results saved to test_output_large.json")
    print("="*80)

if __name__ == "__main__":
    run_tests()
