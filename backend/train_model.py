import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
import pickle
import os
import urllib.request
import zipfile

# 1. Download UCI Dataset
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip"
zip_path = "smsspamcollection.zip"
data_path = "SMSSpamCollection"

if not os.path.exists(data_path):
    print("Downloading UCI SMS Spam Dataset...")
    urllib.request.urlretrieve(url, zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall()
    os.remove(zip_path)
    if os.path.exists("readme"):
        os.remove("readme")

# Load UCI data
uci_df = pd.read_csv(data_path, sep='\t', names=['label', 'message'])
uci_df['label'] = uci_df['label'].map({'ham': 0, 'spam': 1})

# 2. Synthetic India-specific Scam Data
synthetic_scams = [
    # KYC / Bank Scams
    "Dear Customer, your SBI account will be blocked today. Please update your PAN card immediately: http://update-kyc.net/sbi",
    "Dear HDFC User, your net banking has been suspended due to pending KYC. Click link to verify: https://bit.ly/hdfc-kyc",
    "Your ICICI bank account is temporarily locked. Complete verification within 24 hours to avoid suspension: http://tinyurl.com/icici-verify",
    "Warning from RBI: Your card is blocked. Please call customer care or visit this link to reactivate.",
    
    # OTP / Credential Scams
    "Do not share your OTP with anyone. Your OTP for transaction of Rs 50,000 is 439281.",
    "Dear User, your electricity bill is pending and power will be cut off tonight at 9 PM. Please pay immediately or call 9876543210. Provide the OTP received.",
    "Please share the OTP sent to your mobile number to confirm your Amazon delivery. The delivery date is today.",
    
    # Reward / Lottery / Cashback
    "Congratulations! You have won a cash prize of Rs 1,00,000 in the Jio Lucky Draw. Click here to claim your reward: http://jio-prize.claim.com",
    "You have received a cashback of 5000 Rs in your Paytm wallet. Scratch the card to claim your money: https://paytm-cash.in",
    "Your KBC lottery number is 8849. You have won 25 Lakhs. Contact the manager immediately on WhatsApp number +91XXXXXX.",
    
    # Job/Task Scams
    "Work from home and earn Rs 3000-5000 daily by simply liking YouTube videos. Message us on WhatsApp to start.",
    "Urgent hiring for online part-time job. No investment required. Salary 50k/month. Contact HR on WhatsApp link inside.",
    
    # Courier / Post Scams
    "Your India Post package is stuck at the warehouse due to an incomplete address. Update address and pay Rs 10 fee here: http://india-post-tracking.co",
    "BlueDart: Your parcel delivery failed. Please reschedule your delivery and pay the pending customs fee of Rs 45. Link: bit.ly/bluedart",
    
    # Government/Tax Scams
    "Income Tax Department: Based on your recent transactions, an arrest warrant has been issued against you. Pay the penalty to avoid legal action.",
    "Your Aadhaar is linked to illegal activities. The police will block all your bank accounts unless you verify your identity within 2 hours.",

    # Family Emergency Scams (WhatsApp style)
    "Hi mom/dad, my phone broke and I am using a friend's number. Please send Rs 5000 urgently to this UPI as I am stuck.",
    
    # General Phishing
    "Your Netflix subscription has expired. Update your payment details to continue watching: http://netflix-billing-update.com",
    "Your Apple ID has been compromised. Log in securely to reset your password and secure your device.",
     "Dear Customer, your SBI account will be blocked today. Please update your PAN card immediately: http://update-kyc.net/sbi",
    "Dear HDFC User, your net banking has been suspended due to pending KYC. Click link to verify: https://bit.ly/hdfc-kyc",
    "Your ICICI bank account is temporarily locked. Complete verification within 24 hours to avoid suspension: http://tinyurl.com/icici-verify",
    "Warning from RBI: Your card is blocked. Please call customer care or visit this link to reactivate.",
    "Do not share your OTP with anyone. Your OTP for transaction of Rs 50,000 is 439281.",
    "Dear User, your electricity bill is pending and power will be cut off tonight at 9 PM. Please pay immediately or call 9876543210. Provide the OTP received.",
    "Please share the OTP sent to your mobile number to confirm your Amazon delivery. The delivery date is today.",
    "Congratulations! You have won a cash prize of Rs 1,00,000 in the Jio Lucky Draw. Click here to claim your reward: http://jio-prize.claim.com",
    "You have received a cashback of 5000 Rs in your Paytm wallet. Scratch the card to claim your money: https://paytm-cash.in",
    "Your KBC lottery number is 8849. You have won 25 Lakhs. Contact the manager immediately on WhatsApp number +91XXXXXX.",
    "Work from home and earn Rs 3000-5000 daily by simply liking YouTube videos. Message us on WhatsApp to start.",
    "Urgent hiring for online part-time job. No investment required. Salary 50k/month. Contact HR on WhatsApp link inside.",
    "Your India Post package is stuck at the warehouse due to an incomplete address. Update address and pay Rs 10 fee here: http://india-post-tracking.co",
    "BlueDart: Your parcel delivery failed. Please reschedule your delivery and pay the pending customs fee of Rs 45. Link: bit.ly/bluedart",
    "Income Tax Department: Based on your recent transactions, an arrest warrant has been issued against you. Pay the penalty to avoid legal action.",
    "Your Aadhaar is linked to illegal activities. The police will block all your bank accounts unless you verify your identity within 2 hours.",
    "Hi mom/dad, my phone broke and I am using a friend's number. Please send Rs 5000 urgently to this UPI as I am stuck.",
    "Your Netflix subscription has expired. Update your payment details to continue watching: http://netflix-billing-update.com",
    "Your Apple ID has been compromised. Log in securely to reset your password and secure your device."
]
# duplicating synthetic data to give it slightly more weight
synthetic_scams = synthetic_scams * 5


synthetic_safe = [
    # Safe Transactions/Bank
    "Your account A/C XX1234 has been credited with Rs 5,000 on 12-Oct by employer. Available balance is Rs 10,500.",
    "Your transaction of Rs 400 at Starbucks was successful. Available balance is Rs 9,600.",
    "SBI Alert: E-statement for the month of September has been sent to your registered email ID.",
    "Dear Customer, your credit card bill of Rs 4,500 is due on 15th Nov. Please pay to avoid late fees.",

    # Safe OTPs
    "Your OTP for logging into Swiggy is 8492. Valid for 5 minutes. Do not share.",
    "123456 is your OTP to complete your Amazon order. Please enter this at the checkout.",
    
    # Safe Delivery/Services
    "Your Zepto order #ZP123 is out for delivery. Our partner will reach your location in 10 mins.",
    "Your flight 6E-123 is on time and will depart from Terminal 2 at 14:00. Have a safe journey!",
    "Your Uber ride is arriving in 5 minutes. Driver: Rahul. Vehicle: DL1Z 1234.",

    # Safe Personal/Conversations
    "Hey, are we still meeting for dinner tonight at 8?",
    "Can you please send me the presentation file when you get a chance?",
    "Happy Birthday! Hope you have a great day.",
    "I'll be reaching the office 10 minutes late today due to traffic."
]
synthetic_safe = synthetic_safe * 5


synth_df = pd.DataFrame({
    'label': [1] * len(synthetic_scams) + [0] * len(synthetic_safe),
    'message': synthetic_scams + synthetic_safe
})

# -- Dynamic Feedback Injection --
import sqlite3
DB_PATH = os.path.join(os.path.dirname(__file__), "database/fraud_knowledge.db")

final_df = pd.concat([uci_df, synth_df], ignore_index=True)

try:
    conn = sqlite3.connect(DB_PATH)
    feedback_df = pd.read_sql_query("SELECT message, user_correction as label FROM feedback", conn)
    conn.close()
    
    # Map high=1, low=0
    feedback_df['label'] = feedback_df['label'].map({'High': 1, 'Medium': 1, 'Low': 0})
    feedback_df = feedback_df.dropna() # safety
    
    if not feedback_df.empty:
        print(f"Injecting {len(feedback_df)} user feedback rows into training loop...")
        # Weight user feedback very highly by duplicating it
        feedback_df = pd.concat([feedback_df]*10, ignore_index=True)
        final_df = pd.concat([final_df, feedback_df], ignore_index=True)
except Exception as e:
    print(f"No dynamic feedback loaded (or first run): {e}")

# Compile final dataset
final_df = final_df.dropna(subset=['message', 'label']).reset_index(drop=True)

# 3. Train Model with Sentence Transformers (Semantic Embeddings)
print("Loading Sentence Transformer model (this may take a minute on first run)...")
# 'all-MiniLM-L6-v2' is widely used: incredibly fast, 384 dimensional output
transformer = SentenceTransformer('all-MiniLM-L6-v2')

print("Generating text embeddings...")
X = transformer.encode(final_df['message'].tolist(), show_progress_bar=True)
y = final_df['label']

# Train regression on the dense embeddings
print("Training Logistic Regression on Dense Embeddings...")
model = LogisticRegression(solver='liblinear', class_weight='balanced')
model.fit(X, y)

# 4. Save Models
print("Saving Model Components...")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
os.makedirs(MODEL_DIR, exist_ok=True)

# We do NOT save the transformer using pickle (it's loaded via HuggingFace hub dynamically)
# We only need to save the Logistic Regression model that sits on top of it.
with open(os.path.join(MODEL_DIR, "classifier.pkl"), "wb") as f:
    pickle.dump(model, f)

print(f"Done! Classifier artifact saved in {MODEL_DIR}")
