# 🛡️ Digital Fraud Awareness Platform

A full-stack, AI-powered system designed to analyze SMS, WhatsApp, and Email messages to detect phishing, scams, and fraudulent intent. 

The platform utilizes a **Hybrid Detection Engine**, combining the precision of deterministic Rules/Regex with the contextual understanding of a Machine Learning NLP model powered by Sentence Transformers.

![FraudGuard Interface](/docs/hero.png) *(Add a screenshot here)*

## 🚀 Key Features

*   **Hybrid Scoring Engine:** Blends active regex-based heuristic rules with a Logistic Regression ML model to ensure zero-day threats are caught by AI, while known threats are instantly blocked by mathematical rules.
*   **Advanced NLP:** Uses `sentence-transformers` (`all-MiniLM-L6-v2`) to generate dense vector embeddings of messages instead of sparse keyword matrices, allowing the model to understand the *meaning* of a scam rather than just memorizing keywords.
*   **Dynamic Learning Loop:** Features an integrated feedback loop where users can correct the AI. Misclassified messages are saved to a SQLite database and can be automatically re-trained into the model via the Admin panel.
*   **Enterprise UI:** A stunning, institutional-grade React frontend built with Tailwind CSS v4, featuring slide-in animations, dynamic confidence badging, and an expandable "Safety Breakdown" transparency layer.
*   **Real-time Admin Dashboard:** A dedicated interface (`/admin`) to hot-swap, add, delete, and toggle Regex evaluation rules on the fly, instantly changing the scoring math without restarting the server.
*   **Silent Audit Logging:** Asynchronously logs all incoming message analysis requests, scores, processing times, and timestamps to a database for admin monitoring.

## 🛠️ Technology Stack

**Frontend:**
*   React (Vite)
*   Tailwind CSS v4 (Institutional / Financial Theme tokens)
*   Lucide React (Icons)
*   Axios

**Backend:**
*   Python 3.10
*   FastAPI & Uvicorn (Async API)
*   Scikit-Learn & Pandas (Machine Learning)
*   Sentence-Transformers (HuggingFace embeddings)
*   SQLite3 (Relational Database for Rules, Feedback, and Logs)

## 📂 Project Structure

```text
├── backend/
│   ├── admin/
│   │   └── rules.json          # Dynamic rule definitions
│   ├── database/
│   │   ├── db.py               # SQLite connection and schemas
│   │   └── fraud_knowledge.db  # Runtime database (ignored in git)
│   ├── engine/
│   │   ├── hybrid.py           # Core calibration and tiering math
│   │   ├── ml_engine.py        # Connects to the serialized ML Model
│   │   └── rule_engine.py      # Executes regex/keyword rules
│   ├── model/
│   │   └── classifier.pkl      # Pre-trained Logistic Regression model
│   ├── main.py                 # FastAPI endpoints
│   ├── train_model.py          # Script to generate dataset and train model
│   ├── requirements.txt        # Backend dependencies
│   └── Dockerfile              # Containerization for production
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.jsx        # User-facing scanner
│   │   │   └── Admin.jsx       # Rule configuration & management
│   │   ├── App.jsx             # React Router and Layout
│   │   └── index.css           # Tailwind v4 Theme Configuration
│   ├── vercel.json             # Vercel SPA routing
│   └── package.json
└── README.md
```

## 💻 Local Development Setup

### 1. Backend Setup
Navigate to the `backend` directory and set up your Python environment:

```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

**Generate the Initial ML Model & Database:**
Before running the server, you must train the initial Machine Learning model. This script will download datasets, build the `.pkl` file, and initialize the SQLite database:
```bash
python train_model.py
```

**Start the FastAPI Server:**
```bash
python -m uvicorn main:app --reload --port 8000
```
The API will be available at `http://localhost:8000`.

### 2. Frontend Setup
Open a new terminal window, navigate to the `frontend` directory, and start the Vite development server:

```bash
cd frontend
npm install
npm run dev
```
The application will be available at `http://localhost:5173`.

---

## 🚢 Deployment

This platform is architected to be deployed in a decoupled manner: the Frontend as a static SPA, and the Backend as a persistent Docker container.

### Deploying the Frontend (Vercel)
1. Push your code to GitHub.
2. Import the `frontend` folder into Vercel.
3. Vercel will automatically detect Vite. 
4. **Crucial:** Add an Environment Variable in Vercel:
   *   Name: `VITE_API_URL`
   *   Value: `https://your-deployed-backend-url.com`
5. The included `vercel.json` will automatically handle React Router fallbacks.

### Deploying the Backend (Render / Railway / Fly.io)
Because the backend requires continuous disk access for the SQLite database (`fraud_knowledge.db`) and substantial RAM for `sentence-transformers`, serverless functions (like AWS Lambda or Vercel Functions) are strictly prohibited.

Instead, deploy the backend as a Docker container:
1. Connect your GitHub repository to a service like Render or Railway.
2. Select the `backend` folder as the root.
3. The provided `Dockerfile` will automatically install dependencies, bake the 120MB HuggingFace model into the image during the build phase (preventing boot timeouts), and expose Uvicorn on `0.0.0.0:8000`.
4. **Important:** Ensure you attach a "Persistent Volume" to your deployment and map it to `/app/database` so that your SQLite logs and dynamic rules are not destroyed upon container restart.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request to add new advanced Regex Rules to the default dataset or improve UI calibration.
