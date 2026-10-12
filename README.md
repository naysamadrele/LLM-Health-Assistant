# Explainable Clinical Decision Support System (CDSS) for General Health Assessment

A production-grade, local, explainable **Clinical Decision Support System (CDSS)** designed for general health screening, differential diagnosis, and clinical report generation. The system combines:
1. **Rule Engine**: Evaluates clinical vital signs and symptoms to flag critical emergencies (e.g., stroke, cardiac events, hypoxia).
2. **Machine Learning Classifiers**: Predicts risks for **Diabetes**, **Heart Disease**, **Stroke**, and **Chronic Kidney Disease (CKD)** using serialized XGBoost and RandomForest classifiers.
3. **Explainable AI (SHAP)**: Explains the exact drivers behind each risk prediction, translating SHAP feature attributions into natural language insights.
4. **Retrieval-Augmented Generation (RAG)**: Indexes public clinical reference guidelines (from ADA, ACC/AHA, KDIGO, NHS, WHO) into local vector store **ChromaDB** using **sentence-transformers**, and queries a local **Llama 3** model (via **Ollama**) to compile evidence-grounded reports.
5. **Secure Dashboard & PDF Engine**: A premium, responsive dashboard built in React.js and Tailwind CSS featuring secure JWT auth, clinical timelines, interactive SHAP graphs, and one-click PDF report export.

---

## 🛠️ Technology Stack

- **Frontend**: React.js (Vite), Tailwind CSS, Lucide Icons, Chart.js
- **Backend API**: FastAPI, SQLAlchemy, Uvicorn, Pydantic
- **Machine Learning**: XGBoost, Scikit-learn, SHAP
- **Vector DB & NLP**: ChromaDB, sentence-transformers (`all-MiniLM-L6-v2`)
- **LLM Engine**: Ollama running `llama3:8b-instruct-q4_K_M` locally
- **Database**: PostgreSQL (Production) / SQLite (Dev & Test fallback)
- **Containerization**: Docker, Docker Compose, Nginx

---

## 🏗️ Architecture Design

```
                                  +------------------------------+
                                  |    React.js Dashboard        |
                                  |  (HTML5 / Tailwind / Canvas) |
                                  +--------------+---------------+
                                                 ^
                                                 | (HTTPS / JWT Tokens)
                                                 v
                                  +--------------+---------------+
                                  |     Nginx Reverse Proxy      |
                                  +--------------+---------------+
                                                 ^
                                                 |
                                                 v
                                  +--------------+---------------+
                                  |    FastAPI Python Service    |
                                  +-------+---+----+------+------+
                                          |   |    |      |
        +---------------------------------+   |    |      +--------------------------------+
        |                                     |    |                                       |
        v                                     v    v                                       v
+-------+-------+                      +------+----+-----+                         +-------+-------+
|  PostgreSQL   |                      |  Rule Engine    |                         |   ChromaDB    |
| (Audit Logs / |                      | (Priority, Vitals|                         | (Vector Guideline|
| Patient Info) |                      | Red Flags)      |                         | References)   |
+---------------+                      +-----------------+                         +---------------+
                                               ^
                                               |
                                               v
                                       +-------+---------+                         +---------------+
                                       |   ML Pipeline   |                         |  Ollama LLM   |
                                       | (XGBoost/Sklearn| <---------------------> |   (Llama 3    |
                                       |  + SHAP Expl.)  |                         |  Local RAG)   |
                                       +-----------------+                         +---------------+
```

---

## 📂 Project Directory Structure

```
├── backend/
│   ├── Dockerfile                  # Slim Python runner container
│   ├── requirements.txt            # Python ML and API dependencies
│   └── app/
│       ├── main.py                 # FastAPI application entrypoint
│       ├── api/                    # Endpoints (auth, patients, assessments, symptoms)
│       ├── core/                   # Security, configs, and JWT utilities
│       ├── db/                     # SQLAlchemy models, sessions, seeds
│       ├── engine/                 # Clinical red-flags rules engine
│       ├── ml/                     # Dataset generators, training scripts, pipelines, SHAP
│       ├── rag/                    # ChromaDB persistent indexes and Ollama clients
│       └── services/               # Styled ReportLab PDF generation service
├── frontend/
│   ├── Dockerfile                  # Multi-stage production React builder
│   ├── nginx.conf                  # Local container reverse proxy
│   ├── package.json                # Frontend package dependencies
│   ├── tailwind.config.js          # Tailwind theme configurations
│   └── src/
│       ├── main.jsx                # React mount entry
│       ├── index.css               # Tailwind directives and base stylings
│       └── App.jsx                 # Single Page Application core
├── docker/
│   └── nginx.conf                  # Root gateway reverse proxy config
├── docker-compose.yml              # Coordinates postgres, ollama, backend, frontend, nginx
└── README.md                       # Systems guide
```

---

## ⚡ Setup & Run Locally (Fast Development Setup)

### Prerequisites
1. **Python 3.10+** and **Node.js 18+** installed on host machine.
2. **Ollama** installed locally (https://ollama.com).
3. Pull the Llama 3 model:
   ```bash
   ollama pull llama3:8b-instruct-q4_K_M
   ```

### 1. Backend Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run database migrations, symptom seeding, ML model training, and guideline ingestion:
   ```bash
   # Seeds 100+ symptoms
   python -m backend.app.db.seeds.seed_symptoms
   # Trains Diabetes, Heart Disease, Stroke, and CKD Classifiers
   python -m backend.app.ml.train_models
   # Indexes CDC/WHO/NHS reference data in ChromaDB
   python -m backend.app.rag.kb_ingest
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
   ```

### 2. Frontend Setup
1. Open a new terminal in the `frontend/` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:5173`. Toggle Dark Mode in Settings!

---

## 🐳 Production Deployment via Docker Compose

To build and run the entire multi-container environment (PostgreSQL, Ollama, FastAPI, React, and Nginx reverse proxy) locally:

1. Start docker:
   ```bash
   docker compose up --build
   ```
2. What happens automatically:
   - Starts PostgreSQL (`db`) with volume persistence.
   - Starts Ollama (`ollama`) and pulls `llama3:8b-instruct-q4_K_M` via the `ollama-model-pull` sidecar container.
   - Starts FastAPI backend (`backend`), seeds symptoms, trains ML classifiers, embeds guidelines, and listens on port 8000.
   - Starts React frontend (`frontend`), bundles static assets, and hosts them inside Nginx on port 80.
3. Access the entire app on **`http://localhost`** (port 80).

---

## ☁️ Cloud VM Deployment Guide (AWS EC2 / Azure VM / Google Cloud Compute Engine)

This production configuration runs Nginx with automated Let's Encrypt SSL certificates.

### 1. Firewall Configuration (Security Groups)
Expose only these ports on the cloud VM:
- **Port 22 (TCP)**: SSH access (restricted to your IP).
- **Port 80 (TCP)**: HTTP (automatically redirected to HTTPS).
- **Port 443 (TCP)**: HTTPS (secure TLS entrypoint).

### 2. Install Docker & Docker Compose on the host VM
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get install docker-compose-plugin -y
```

### 3. Deploy and Set Up Let's Encrypt HTTPS
For production, update `docker-compose.yml` to replace the local frontend build with a production Nginx gateway routing certificate challenges.
1. Install certbot on host:
   ```bash
   sudo apt-get install certbot python3-certbot-nginx -y
   ```
2. Request a certificate:
   ```bash
   sudo certbot certonly --standalone -d yourdomain.com
   ```
3. Mount the certificates into your Nginx reverse proxy container:
   - Private key: `/etc/letsencrypt/live/yourdomain.com/privkey.pem`
   - Certificate: `/etc/letsencrypt/live/yourdomain.com/fullchain.pem`
4. Set up a daily cron tab to auto-renew certs:
   ```bash
   echo "0 0 * * * certbot renew --post-hook 'docker compose restart nginx'" | sudo tee -a /var/spool/cron/crontabs/root
   ```

---

## 📝 Medical Disclaimer

**IMPORTANT**: This system is a **Clinical Decision Support System (CDSS)** meant to assist licensed healthcare providers. The results, predictions, and guidelines compiled by the machine learning models and the Retrieval-Augmented Generation (RAG) pipeline are for analytical workspace support only. They do not constitute final clinical diagnoses. Clinical outcomes must be verified with laboratory work, clinical checks, and diagnostic evaluations.
