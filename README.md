# AI Database Analyst

An AI-first data analysis platform combining FastAPI, LangGraph, ChromaDB, and a future React + Vite frontend for intelligent database querying and document-assisted analytics.

---

## 1. Project Structure

```
AI_DATABASE_ANALYST/
├── backend/
│   ├── app/                  # FastAPI core application, routers, services, AI workflows
│   ├── migrations/           # Alembic database migrations
│   ├── storage/              # Local storage: uploads/ and chroma/ vector index
│   ├── tests/                # Test suite (automated unit/integration tests & manual scripts)
│   ├── .env                  # Backend environment secrets
│   ├── .env.test             # Test environment variables
│   ├── alembic.ini           # Alembic configuration
│   ├── pytest.ini            # Pytest configuration
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # Future React + Vite user interface
│
├── aienv/                    # Python virtual environment (Windows)
├── .gitignore                # Global gitignore covering backend & frontend
└── README.md
```

---

## 2. Backend Development & Execution

All backend commands are run from the `backend/` directory using the project virtual environment.

### A. Environment Setup & Installation
```powershell
cd backend
..\aienv\Scripts\activate
pip install -r requirements.txt
```

### B. Running the FastAPI Server
```powershell
cd backend
..\aienv\Scripts\uvicorn app.main:app --reload
```
API Documentation will be available at `http://127.0.0.1:8000/docs`.

### C. Database Migrations (Alembic)
```powershell
cd backend
..\aienv\Scripts\alembic upgrade head
..\aienv\Scripts\alembic check
```

---

## 3. Testing & Verification

### A. Automated Test Suite (Pytest)
Run the automated test suite across Auth, Encryption, External Databases, PDF Extraction, and Tables:
```powershell
cd backend
..\aienv\Scripts\pytest -v
```

Run specific modules:
```powershell
cd backend
..\aienv\Scripts\pytest tests/test_auth.py -v
..\aienv\Scripts\pytest tests/test_pdf_document_processing.py tests/test_pdf_table_processing.py -v
..\aienv\Scripts\pytest tests/test_encryption.py tests/test_external_database.py -v
```

### B. Manual Verification & Benchmark Scripts
Run standalone scripts using module mode (`python -m`):
```powershell
cd backend

# Inspect ChromaDB stored vector embeddings
..\aienv\Scripts\python -m tests.test_view_vectors

# RAG Performance Benchmark
..\aienv\Scripts\python -m tests.rag_performance

# Interactive PDF Processing CLI
..\aienv\Scripts\python -m tests.pdf_processing_manual

# Interactive PDF Table Extraction CLI
..\aienv\Scripts\python -m tests.pdf_tables_manual
```

---

## 4. Frontend Development (Upcoming)

To scaffold the React + Vite frontend inside `frontend/`:
```powershell
cd frontend
npm create vite@latest .
npm install
npm run dev
```
