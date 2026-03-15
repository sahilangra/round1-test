# 🤖 AI Leadership Insight & Decision Agent

An advanced, RAG-powered assistant designed to assist executive leadership and stakeholders. This agent analyzes internal organization documents (PDFs) to provide concise, factual insights and data visualizations grounded strictly in private company data.

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | Streamlit |
| **Orchestration** | LangChain |
| **LLM** | Google Gemini 2.5 Flash |
| **Vector DB** | ChromaDB (Local) |
| **Embeddings** | HuggingFace (Local `sentence-transformers`) |
| **Observability**| Langfuse |

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python **
- A **Google Gemini API Key** (Get one at [Google AI Studio](https://aistudio.google.com/))
- (Optional) **Docker & Docker Compose** (For local Langfuse hosting)

### 2. Installation
Clone the repository and install the pinned dependencies:

```bash
# Clone the repo
git clone <repository_url>
cd Adobe-test

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Setup Observability (Optional)
To enable tracing and monitoring, you can run a local instance of Langfuse:

1.  Follow the [Langfuse Self-Hosting Guide](https://langfuse.com/self-hosting/deployment/docker-compose). [ optional ]
2.  Quick start with Docker Compose:
    ```bash
    # Run in a separate terminal
    docker-compose up -d
    ```
3.  Access the dashboard at `http://localhost:3000`.
4.  Create a project and obtain your `Public Key`, `Secret Key`, and `Base URL`.

### 4. Configuration
Create a `.env` file in the project root:

```bash
# Copy the example
cp .env.example .env
```

Edit the `.env` file with your credentials:
```ini
GEMINI_API_KEY="your_google_ai_key"

# Langfuse Settings (Optional)
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_BASE_URL="http://localhost:3000"
```

---

## 📖 Usage

1.  **Run the App:**
    ```bash
    streamlit run app.py
    ```
2.  **Ingest Documents:**
    - Navigate to the **"Ingestion"** page.
    - Upload your Annual Reports, Quarterly Updates, or Strategy PDFs. 
    - Click **"Process Documents"**.
3.  **Start Querying:**
    - Navigate to the **"Inference"** page.
    - Ask strategic questions like: *"What was our revenue growth in FY2023 compared to FY2024?"* or *"Summarize the risk factors mentioned in the latest Q3 report."*
3.  **Observability**
    - Head over to Langfuse dashboard at `http://localhost:3000`.
    - You can see the traces of every LLM call and document ingestion event.
    - Enable evaluation and run evals to evaluate the model performance on the go.
---
