# Hybrid Log Classification System

An enterprise-grade, 3-tier hybrid log monitoring and classification backend designed to categorize raw software logs into functional domains (e.g., `Security Alert`, `Resource Usage`, `Workflow Error`, `System Notification`, `HTTP Status`). 

By cascading inference across **Python Regular Expressions**, **BERT (MiniLM) Embeddings + Logistic Regression**, and **LLMs (Llama 3.3 / DeepSeek R1)**, this system optimizes cost, maximizes execution speed, and maintains high classification accuracy.

This repository implements the exact architecture highlighted in the candidate's resume:

* **3-Tier Hybrid Pipeline**: Architected a cascading classification engine combining **Python RegEx**, **Sentence-Transformers (`all-MiniLM-L6-v2`) + Logistic Regression**, and **LLMs (Llama 3.3 / DeepSeek R1)** to drastically minimize API token expenses and reduce end-to-end latency.
* **Unsupervised Pattern Discovery**: Extracted recurring log structures by clustering 384-dimensional sentence transformer embeddings using **DBScan**, enabling automated RegEx rule generation that covered **500+ log lines**.
* **Production REST API**: Deployed a real-time log processing backend using **FastAPI** and **Uvicorn**, with serialized Scikit-Learn models served via **Joblib**.

---

## 🏗 System Architecture

The classification pipeline routes log messages through three distinct processing tiers based on pattern predictability and sample availability:

```
                      +-------------------+
                      |   Incoming Log    |
                      +---------+---------+
                                |
                                v
                   +--------------------------+
                   |  Tier 1: RegEx Processor |
                   +------------+-------------+
                                |
                   +------------+------------+
                   |                         |
              (Match Found)             (No Match / Unknown)
                   |                         |
                   v                         v
        +--------------------+    +--------------------+
        | Return Category    |    | Sample Count Check |
        | (Fastest & Free)   |    +----------+---------+
        +--------------------+               |
                               +-------------+-------------+
                               |                           |
                       (< 5 Samples)               (>= 5 Samples)
                               |                           |
                               v                           v
                  +-------------------------+  +-------------------------+
                  | Tier 3: LLM Processor   |  | Tier 2: BERT Processor  |
                  | (Llama 3.3 / DeepSeek)  |  | (Embedding + LogReg)    |
                  +------------+------------+  +------------+------------+
                               |                           |
                               +-------------+-------------+
                                             |
                                             v
                                   +-------------------+
                                   | Final Category /  |
                                   | Unclassified      |
                                   +-------------------+
```

### Routing Logic

1. **Tier 1 — RegEx Matching (High Speed, Zero Cost)**: Fixed log patterns (e.g., user logins, file uploads, routine system starts) are processed instantly using compiled regular expressions.
2. **Tier 2 — BERT + Logistic Regression (High Throughput, Low Cost)**: For complex logs with sufficient training data ($\ge 5$ samples), the log text is converted into a 384-dimensional dense vector via `all-MiniLM-L6-v2` and classified using a pre-trained **Logistic Regression** model (`log_classifier.joblib`). Probability thresholds ($P > 0.5$) prevent false positives.
3. **Tier 3 — LLM Inference (Zero-Shot / Few-Shot Reasoning)**: Sparse or rare log categories with insufficient training samples (e.g., `Legacy CRM` errors, deprecation warnings, workflow anomalies) are routed to **Llama 3.3 70B** (via Groq API) or **DeepSeek R1** (via local Ollama).

---

## 🛠 Tech Stack & Tools

* **Programming Language**: Python 3.10+
* **Machine Learning & NLP**: Scikit-Learn, PyTorch, Sentence-Transformers (`all-MiniLM-L6-v2`), DBScan, Joblib
* **LLM Orchestration**: Groq API (`llama-3.3-70b-versatile`), Ollama (`deepseek-r1:7b`), OpenAI Python SDK
* **Backend Framework**: FastAPI, Uvicorn, Pydantic
* **Data Processing & Analytics**: Pandas, NumPy, Regex (`re`)
* **Development Environment**: PyCharm Professional / VS Code

---

## 📂 Directory Structure

```text
log-classification/
├── .env                       # API keys (GROQ_API_KEY)
├── .gitignore                 # Excluded files (.env, __pycache__, models/)
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── classify.py                # Main hybrid classification router logic
├── processor_regex.py         # Tier 1: RegEx pattern matcher
├── processor_bert.py          # Tier 2: Sentence-Transformers + Logistic Regression
├── processor_llm.py           # Tier 3: Groq / Ollama LLM client
├── server.py                  # FastAPI REST server implementation
├── models/
│   └── log_classifier.joblib  # Serialized Logistic Regression model
├── resources/
│   ├── test.csv               # Sample input CSV for bulk inference
│   └── architecture_diagram.png
└── training/
    ├── data_set/
    │   └── synthetic_logs.csv # Aggregated training dataset
    └── training.ipynb         # DBScan clustering & model training notebook
```

---

## 🚀 Getting Started

### 1. Prerequisites

Ensure you have Python 3.10+ installed. Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/your-username/log-classification-system.git
cd log-classification-system
```

### 2. Environment Setup

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. API Key Configuration

Create a `.env` file in the root directory and add your Groq API key:

```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

*(Note: If using local Ollama instead, ensure the Ollama service is running on `http://localhost:11434` with `deepseek-r1:7b` pulled).*

---

## 💻 Usage & Execution

### Running the FastAPI Server

Launch the backend API server using Uvicorn:

```bash
uvicorn server:app --reload --port 8000
```

The server will start at `http://127.0.0.1:8000`. You can inspect the interactive OpenAPI documentation at `http://127.0.0.1:8000/docs`.

### API Endpoint: Bulk CSV Classification

**Endpoint**: `POST /classify`

**Curl Example**:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/classify' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@resources/test.csv'
```

**Response**: Returns an output CSV file containing the original `Source` and `Log Message` along with the predicted `Target Label`.

---

## 📊 Model Training & Unsupervised Clustering

To re-train the BERT + Logistic Regression model or discover new RegEx patterns:

1. Open `training/training.ipynb` in PyCharm or Jupyter Notebook.
2. **DBScan Clustering**: Converts log lines to embeddings and clusters them to reveal frequent fixed log formats.
3. **Model Export**: Trains the Scikit-Learn Logistic Regression model on labeled log messages and dumps the binary artifact to `models/log_classifier.joblib`.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
