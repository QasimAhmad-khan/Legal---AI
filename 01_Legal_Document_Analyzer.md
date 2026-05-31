# Project 1 — AI-Powered Legal Document Analyzer

**Stack:** Next.js (App Router) · FastAPI · Provider-agnostic LLM API · PostgreSQL + pgvector
**Type:** Full-stack SaaS · GitHub portfolio showcase
**One-liner:** A SaaS app that lets law firms upload contracts and receive AI-generated clause summaries, risk flags, and compliance checks, grounded in their own precedent documents via RAG.

---

## 1. Detailed Brief

### Problem
Legal teams spend hours manually reviewing contracts for risky clauses, missing obligations, and deviations from their own standard playbooks. Generic LLM tools hallucinate legal facts and don't know a firm's internal precedent.

### Solution
A web application where a user uploads a contract (PDF/DOCX). The backend extracts text, chunks it, and runs a **structured prompt chain** that produces: (1) a plain-English clause-by-clause summary, (2) a risk-flag report scored by severity, and (3) a compliance check against a configurable ruleset. A **RAG pipeline** retrieves the firm's own precedent clauses from a pgvector store so answers are grounded in firm-specific language rather than invented.

### Why it's portfolio-worthy
It demonstrates: RAG architecture, vector search, multi-step LLM orchestration (prompt chaining), document parsing, auth + RBAC, streaming UI, and a clean provider-agnostic AI layer. These are exactly the skills hiring managers screen for in 2025–2026 AI engineering roles.

### Target users
- **Associate / paralegal** — uploads contracts, reads summaries and flags.
- **Partner / admin** — manages the precedent library, configures compliance rules, manages team access.

### Core value metrics (to show on the README)
- Reduced hallucination rate via grounding (measure with an eval set — see To-Do).
- Time-to-first-summary (streaming).
- % of risky clauses correctly flagged on a labeled test set.

### Provider-agnostic AI note
**Do not hardcode any single LLM vendor.** All model calls go through one `LLMProvider` interface. Implementations: OpenAI, Anthropic, Google Gemini, Mistral, and a local Ollama option. The active provider is chosen via env var (`LLM_PROVIDER`). Embeddings likewise go through an `EmbeddingProvider` interface (OpenAI `text-embedding-3`, or local `bge`/`nomic` via Ollama, or `sentence-transformers`).

### Out of scope (v1)
Real legal advice/guarantees (add a disclaimer banner), e-signature, billing/payments, multi-language contracts.

---

## 2. Product Requirements Document (PRD)

### 2.1 Goals
| # | Goal | Success criterion |
|---|------|-------------------|
| G1 | Upload & parse contracts | PDF/DOCX up to 50 pages parsed to clean text in <15s |
| G2 | Clause summaries | Each detected clause has a ≤3-sentence plain-English summary |
| G3 | Risk flags | Flags rated Low/Medium/High with cited source span |
| G4 | Compliance check | Pass/fail against a user-defined rule list, with rationale |
| G5 | RAG grounding | Summaries cite retrieved precedent chunks; measurable hallucination drop |
| G6 | Auth + RBAC | JWT auth; roles `admin`, `member`; precedent library admin-only writeable |
| G7 | Streaming UX | Responses stream token-by-token into the dashboard |

### 2.2 Functional requirements
1. **Document ingestion** — accept PDF/DOCX, extract text, detect clause boundaries (heading/numbered-section heuristics + LLM fallback), store document + chunks.
2. **Embedding & indexing** — chunk precedent docs, embed, store vectors in pgvector with metadata (doc id, clause type, source span).
3. **Analysis pipeline (prompt chain)**:
   - Step A: classify clauses (e.g., indemnity, termination, liability cap, governing law).
   - Step B: for each clause, retrieve top-k precedent chunks (RAG).
   - Step C: generate grounded summary + risk score + compliance verdict, returning structured JSON.
4. **Risk report** — aggregate per-clause flags into a document-level report.
5. **Compliance rules** — admin defines rules (natural-language statements); engine checks each against the contract.
6. **Dashboard** — list documents, view analysis, stream live, export report (Markdown/PDF).
7. **Precedent library management** — admin uploads/removes precedent docs (re-indexes automatically).

### 2.3 Non-functional
- Provider-agnostic LLM + embedding adapters.
- Stateless FastAPI; horizontal-scalable.
- All AI outputs validated against a JSON schema; retry-on-invalid.
- Audit log of every analysis run.
- Secrets via env only; never commit keys.

### 2.4 Data model (PostgreSQL)
- `users(id, email, hashed_pw, role, org_id, created_at)`
- `orgs(id, name)`
- `documents(id, org_id, filename, type, status, uploaded_by, created_at)`
- `chunks(id, document_id, text, char_start, char_end, clause_type, embedding vector)`
- `precedents(id, org_id, filename, created_at)`
- `precedent_chunks(id, precedent_id, text, clause_type, embedding vector)`
- `analyses(id, document_id, summary_json, risk_json, compliance_json, model_used, created_at)`
- `compliance_rules(id, org_id, text, active)`
- `audit_log(id, user_id, action, payload, created_at)`

### 2.5 API surface (FastAPI)
- `POST /auth/register`, `POST /auth/login` → JWT
- `POST /documents` (upload) · `GET /documents` · `GET /documents/{id}`
- `POST /documents/{id}/analyze` → streams analysis (SSE)
- `GET /documents/{id}/report?format=md|pdf`
- `POST /precedents` (admin) · `DELETE /precedents/{id}` (admin)
- `GET /compliance-rules` · `POST /compliance-rules` (admin)

### 2.6 Architecture
```
Next.js (Vercel) ── REST/SSE ──> FastAPI
                                   ├─ Parser (pdfplumber / python-docx)
                                   ├─ LLMProvider (swappable)
                                   ├─ EmbeddingProvider (swappable)
                                   ├─ RAG retriever (pgvector)
                                   └─ Pipeline orchestrator (prompt chain)
                                        └─> PostgreSQL + pgvector
```

### 2.7 Milestones
- **M1** Skeleton + auth + DB. **M2** Ingestion + parsing. **M3** Embeddings + pgvector + RAG. **M4** Analysis prompt chain + JSON validation. **M5** Dashboard + streaming. **M6** Compliance rules + reports. **M7** Eval harness + README polish.

---

## 3. To-Do List (agentic-AI ready)

> Tasks are ordered. Each `[HUMAN]` task is something the AI agent should **pause and ask you to do** (downloading data, providing keys, creating accounts). Everything else the agent can do autonomously.

### Phase 0 — Setup
- [ ] Initialize monorepo: `/frontend` (Next.js), `/backend` (FastAPI), `/infra`, `/evals`.
- [ ] **[HUMAN] Provide LLM credentials.** Agent should ask: "Which LLM provider do you want as default? Please create an account at your chosen provider and paste the API key into `backend/.env` as `LLM_API_KEY` and set `LLM_PROVIDER`." (Agent must NOT create accounts itself.)
- [ ] Add `.env.example` with all keys; ensure `.gitignore` excludes `.env`.
- [ ] Set up `docker-compose` with Postgres + pgvector extension enabled.

### Phase 1 — Backend foundation
- [ ] Scaffold FastAPI app, SQLAlchemy models, Alembic migrations for the data model above.
- [ ] Implement JWT auth (register/login), password hashing (bcrypt/argon2), role middleware.
- [ ] Write the `LLMProvider` abstract interface + concrete adapters (OpenAI, Anthropic, Gemini, Mistral, Ollama). Selected via `LLM_PROVIDER` env.
- [ ] Write the `EmbeddingProvider` interface + adapters (API-based + local `sentence-transformers`).
- [ ] Unit-test both adapters with a mock/fake provider.

### Phase 2 — Ingestion
- [ ] Implement upload endpoint; store file to local disk / S3-compatible storage.
- [ ] Parse PDF (`pdfplumber`) and DOCX (`python-docx`) to clean text.
- [ ] Clause segmentation: heuristic (numbered headings) + LLM fallback for unstructured text.
- [ ] Persist `documents` + `chunks`.

### Phase 3 — Precedent data + RAG
- [ ] **[HUMAN] Provide precedent documents.** Agent should ask: "I need sample precedent contracts to build the RAG library. Please either (a) download a public contract dataset and place files in `/backend/data/precedents/`, or (b) tell me to generate synthetic precedents. Recommended public sources: the **CUAD** dataset (Contract Understanding Atticus Dataset, ~510 labeled contracts) on Hugging Face/Atticus Project, or **SEC EDGAR** material contract exhibits. Download steps for CUAD: visit the Atticus Project CUAD page → download the zip → unzip into `/backend/data/precedents/`. Confirm when done."
- [ ] If no real data provided, generate synthetic precedent clauses via the LLM for demo purposes (label them clearly as synthetic).
- [ ] Chunk + embed precedents; store in `precedent_chunks` with pgvector.
- [ ] Build retriever: cosine top-k with metadata filter by clause type.

### Phase 4 — Analysis pipeline
- [ ] Implement prompt chain (classify → retrieve → grounded-generate) returning strict JSON.
- [ ] Add JSON-schema validation + retry-on-invalid + max-retry guard.
- [ ] Implement risk scoring + compliance check (rules pulled from DB).
- [ ] Store results in `analyses`; write `audit_log` entry.
- [ ] Expose SSE streaming endpoint.

### Phase 5 — Frontend
- [ ] Next.js auth pages (login/register), protected routes.
- [ ] Upload UI with progress; document list view.
- [ ] Analysis view: streamed summary, color-coded risk flags, compliance pass/fail with source-span highlights.
- [ ] Admin: precedent library manager + compliance rule editor.
- [ ] Export report (Markdown + PDF) button.
- [ ] Add prominent "Not legal advice" disclaimer.

### Phase 6 — Evaluation (the differentiator)
- [ ] **[HUMAN] Approve eval approach.** Agent asks: "To measure the hallucination-reduction claim, I'll build a small labeled eval set (10–20 contracts with known risky clauses). Should I derive labels from CUAD annotations or have you label them?"
- [ ] Build eval harness in `/evals`: run pipeline with RAG ON vs OFF, score grounding/accuracy, output a metrics table.
- [ ] Record real numbers for the README (replace any guessed percentages with measured ones).

### Phase 7 — Deploy & document
- [ ] **[HUMAN] Deployment accounts.** Agent asks you to create Vercel + a Postgres host (e.g., Neon/Supabase) accounts and paste connection strings; agent will NOT create accounts or accept ToS on your behalf.
- [ ] Deploy frontend (Vercel), backend (Render/Fly/Railway), managed Postgres+pgvector.
- [ ] Write README: architecture diagram, demo GIF, measured metrics, setup instructions, "swap your LLM provider" section.
- [ ] Add architecture decision records (ADRs) and a short demo video link.
