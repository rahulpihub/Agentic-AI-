# 🤖 MoU-GENIUS: Agentic AI-Powered MoU Lifecycle Automation

MoU-GENIUS is a full-stack Agentic AI system designed to automate the **entire lifecycle of Memorandums of Understanding (MoUs)** — from drafting, clause retrieval, and stakeholder communication to approval tracking and version control. Built with multi-agent orchestration using LangGraph and powered by Gemini + ChromaDB.

---

## 🚀 Tech Stack

| Layer        | Stack                                         |
| ------------ | --------------------------------------------- |
| Frontend     | React (TailwindCSS, Vite)                     |
| Backend      | Django + LangGraph                            |
| Vector Store | ChromaDB + SentenceTransformer                |
| Database     | MongoDB (Atlas or Local)                      |
| LLM          | Gemini 1.5 Flash via `langchain_google_genai` |
| Email Agent  | Gmail (App Password Auth)                     |

---

## 🧠 Agentic AI Workflow

| Agent                                  | Function                                                              |
| -------------------------------------- | --------------------------------------------------------------------- |
| 📝 **Agent 1: MoU Drafter**            | Generates professional MoU based on user input using Gemini 1.5.      |
| 📚 **Agent 2: Clause Retriever (RAG)** | Retrieves top-5 legal clauses using ChromaDB + sentence embeddings.   |
| 📬 **Agent 3: Communication Agent**    | Sends MoU + clause suggestions to stakeholders via Gmail.             |
| ✅ **Agent 4: Approval Tracker**        | Tracks stakeholder feedback (Approved/Rejected/Idle) from MongoDB.    |
| 🧮 **Agent 5: Version Controller**     | Compares current vs previous drafts and stores only if changes exist. |

---

## 📁 Project Structure

```
Agentic-AI-/
│
├── backend/
│   ├── langgraph_flow.py        # All agent code + LangGraph pipeline
│   ├── views.py                 # Django API endpoints
│   ├── chroma.py                # RAG ingestion for clauses into ChromaDB
│   └── requirements.txt         # Backend Python dependencies
│
├── frontend/
│   ├── Home.tsx                # MoU generation interface
│   ├── Verification.tsx        # Approval status dashboard
│   └── package.json
│
├── clause_chromadb/           # Vector DB folder (auto-created)
├── clauses.csv                # Source clause data for ingestion
├── .env                       # API keys and secrets
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repo

```bash
git clone https://github.com/rahulpihub/Agentic-AI-.git
cd Agentic-AI-
```

### 2️⃣ Backend Setup

```bash
cd backend
pip install -r requirements.txt
python manage.py runserver
```

> Make sure `.env` file contains:

```env
GEMINI_API_KEY=your_gemini_key
MONGO_URI=your_mongodb_connection_url
GMAIL_APP_PWD=your_gmail_app_password
```

### 3️⃣ Frontend Setup

```bash
cd ../frontend
npm install
npm run dev
```

---

## 🧩 RAG Clause Ingestion (ChromaDB)

Use `chroma.py` to ingest your clause dataset (`clauses.csv`) into ChromaDB:

```bash
python chroma.py
```

This will:

* Read the CSV containing clause data
* Generate embeddings via `all-MiniLM-L6-v2`
* Store them with metadata into `clause_chromadb/` vector DB

---

## 🌐 Frontend Interfaces

* **Home Page (`/`)**: Fill MoU form → Trigger AI workflow → View draft, clauses, email status, approvals, versioning.
* **Approval Page (`/approval`)**: Approvers can update their status (Approved, Idle, Rejected).

---

## 📎 Notes

* Ensure Gmail app password is enabled and SMTP access is allowed.
* Clause retrieval requires `clauses.csv` and successful ChromaDB ingestion.
* Make sure MongoDB is running (Atlas or local) and accessible.

