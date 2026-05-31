# Legal AI - Contract Intelligence

Legal AI is an advanced, AI-powered document analysis platform built to parse, process, and analyze legal contracts. By leveraging Large Language Models (LLMs) and vector embeddings (RAG), it automatically scores legal clauses for risk, compares them against company precedents, and verifies them against compliance rules.

## Features

- **Document Ingestion:** Supports uploading `.txt`, `.pdf`, and `.docx` files.
- **Background Processing:** Asynchronous text extraction and chunking.
- **Retrieval-Augmented Generation (RAG):** Uses `pgvector` to find semantically similar firm precedents.
- **Real-Time Analysis Streaming:** Watch the AI analyze your contract clause-by-clause in real-time via Server-Sent Events (SSE).
- **Provider-Agnostic LLM Layer:** Swap seamlessly between Gemini, OpenAI, and Anthropic.
- **Premium UI:** A highly responsive, dynamic, dark-mode boxy UI built with Next.js and TailwindCSS.

## Tech Stack

- **Frontend:** Next.js (App Router), React, TailwindCSS.
- **Backend:** FastAPI, Python, SQLAlchemy, Pydantic.
- **Database:** PostgreSQL with the `pgvector` extension.
- **AI/LLM:** `google-genai` (Gemini 2.5 Flash), `openai`, `anthropic`.

## Prerequisites

Ensure you have the following installed:
- Docker & Docker Compose (for the PostgreSQL database)
- Python 3.10+
- Node.js 18+

## Quickstart

### 1. Start the Database
The project requires a PostgreSQL database with the `pgvector` extension. A `docker-compose.yml` is provided.
```bash
docker-compose up -d
```

### 2. Run the Backend
Navigate to the `backend` folder, install dependencies, and start the FastAPI server.
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # On Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
*Note: The backend automatically drops and recreates tables on startup if they don't exist.*

### 3. Run the Frontend
Navigate to the `frontend` folder, install Node modules, and start the development server.
```bash
cd frontend
npm install
npm run dev
```

### 4. Usage
Open [http://localhost:3000/auth/register](http://localhost:3000/auth/register) in your browser. Create an account to access the dashboard, upload a legal document, and click "View Analysis" to see the AI in action.

## Environment Variables
In your `backend/.env` file, ensure you have your LLM API keys:
```env
LLM_PROVIDER=gemini  # Or openai, anthropic
LLM_API_KEY=your_api_key_here
DATABASE_URL=postgresql://admin:password@localhost:5432/legal_analyzer
```
