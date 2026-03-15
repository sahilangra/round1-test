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
- A **Google Gemini API Key** 
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

1.  Follow the Langufse self hosting guide. [ optional ]
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
    - Navigate to the **"Inference"** page
3.  **Observability**
    - Head over to Langfuse dashboard at `http://localhost:3000`.
    - You can see the traces of every LLM call and document ingestion event.
    - Enable evaluation and run evals to evaluate the model performance on the go.
---

## 🚀 Future Roadmap & Improvements

To evolve the **AI Leadership Insight & Decision Agent** into a production-grade enterprise solution, the following improvements are planned:

*   **Advanced Prompt Management**: Transition from hardcoded strings to a centralized management system. This will enable seamless prompt versioning, A/B testing, and easier collaboration for prompt engineering.
*   **Enterprise-Grade Secrets Management**: Move beyond `.env` files to robust, cloud-native solutions like **AWS Secrets Manager**, **Azure Key Vault**, or **GCP Secret Manager** to ensure secure handling of API keys and database credentials.
*   **Full Containerization**: Provide a refined `Dockerfile` and `docker-compose.yml` optimized for production environments. This will ensure consistent deployment across staging and production clusters (e.g., Kubernetes).
*   **Multi-Format Document Support**: Expand ingestion capabilities beyond PDFs to include common business formats such as **Microsoft Word (.docx)**, **Excel (.xlsx)**, and **PowerPoint (.pptx)**.
*   **Native Enterprise Connectors**: Implement direct integrations with widespread data silos, including **SharePoint**, **Amazon S3**, **Google Drive**, and **Microsoft OneDrive**, to automate document syncing.
*   **Systemic Agent Hardening**: Increase reliability through automated adversarial testing and systematic prompt evaluation using **Langfuse**. This includes building a specialized "eval set" of leadership questions to monitor quality over time.

---
