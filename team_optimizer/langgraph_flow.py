# team_optimizer/langgraph_flow.py

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_core.tools import tool

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI

import chromadb
from sentence_transformers import SentenceTransformer

import smtplib
from email.mime.text import MIMEText


# ──────────────────────────────────────────────────────────────────────────────
# 1. ENVIRONMENT & DB SETUP
# ──────────────────────────────────────────────────────────────────────────────
load_dotenv()

# LLM for drafting
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7
)

# MongoDB for storing drafts
client = MongoClient(os.getenv("MONGO_URI"))
db = client["AgenticAI"]
draft_collection = db["MoUDrafts"]

# ──────────────────────────────────────────────────────────────────────────────
# 2. CHROMADB VECTOR STORE SETUP (INGESTED ALREADY)
# ──────────────────────────────────────────────────────────────────────────────
# Use the same folder you wrote into when running your ingestion script
chroma_client = chromadb.PersistentClient(path="./clause_chromadb")
clause_collection = chroma_client.get_or_create_collection(name="clauses")

# Sentence-Transformer for embeddings
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ──────────────────────────────────────────────────────────────────────────────
# 3. AGENT 1: MoU Drafting
# ──────────────────────────────────────────────────────────────────────────────
def draft_mou(state: dict):
    """
    Agent 1: Generate the initial MoU draft from intake form.
    """
    print("🔁 Drafting MoU with form data:", state)
    
    prompt = f"""
You are a legal assistant. Create a formal Memorandum of Understanding (MoU) document.

Details:
- Company Name: {state['company_name']}
- Partnership Type: {state['partnership_type']}
- Objective: {state['objective']}
- Scope: {state['scope']}

Respond in professional business language. Format as an MoU.
"""
    response = llm.invoke(prompt)
    draft = response.content.strip()

    # Persist the draft
    draft_collection.insert_one({
        "company_name": state["company_name"],
        "draft": draft,
        "type": state["partnership_type"]
    })
    print("✅ Draft saved to MongoDB.")

    # Return new state with draft_text
    return {
        **state,
        "draft_text": draft
    }

# ──────────────────────────────────────────────────────────────────────────────
# 4. AGENT 2: Clause Retrieval (RAG Agent)
# ──────────────────────────────────────────────────────────────────────────────
# In team_optimizer/langgraph_flow.py

# team_optimizer/langgraph_flow.py (only this function changes)

def retrieve_clauses(state: dict):
    """
    Agent 2: Retrieve top-5 clauses, including their IDs, using raw chromadb client.
    """
    draft = state.get("draft_text", "")
    print("🔎 Retrieving clauses for draft length:", len(draft))

    # 1) Embed the draft
    query_emb = embedder.encode(draft).tolist()

    # 2) Query raw ChromaDB (no include arg needed)
    results = clause_collection.query(
        query_embeddings=[query_emb],
        n_results=5
    )
    #print("🔍 Query results:", results)

    ids       = results["ids"][0]        # List[str]
    texts     = results["documents"][0]  # List[str]
    metadatas = results["metadatas"][0]  # List[dict]

    # 3) Zip into structured list
    retrieved = []
    for i in range(len(ids)):
        retrieved.append({
            "clause_id": ids[i],
            "clause_type": metadatas[i].get("clause_type"),
            "partnership_type": metadatas[i].get("partnership_type"),
            "text": texts[i]
        })

    # print("📚 Retrieved Clauses:", retrieved)
    return {
        **state,
        "retrieved_clauses": retrieved
    }


# ──────────────────────────────────────────────────────────────────────────────
# 5. AGENT 3: Communication Agent
# ──────────────────────────────────────────────────────────────────────────────


@tool
def get_stakeholders_from_db() -> list:
    """Fetches all stakeholders from the 'stakeholders' collection in MongoDB."""

    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["AgenticAI"]
    collection_stakeholders = db["stakeholders"]

    stakeholders = list(collection_stakeholders.find({}, {"_id": 0}))
    print("👥 Retrieved Stakeholders:", stakeholders)
    return stakeholders


@tool(description="Send MoU draft email to a stakeholder using their name, email, and draft content.")
def send_email_to_stakeholder(name: str, email: str, draft_text: str) -> str:
    sender_email = "rahulsnsihub@gmail.com"
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    msg = MIMEText(draft_text)
    msg["Subject"] = "MoU Draft for Review"
    msg["From"] = sender_email
    msg["To"] = email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, app_password)
        server.sendmail(sender_email, [email], msg.as_string())
        server.quit()

        print(f"📨 Real email sent to {email}")
        return f"Email sent to {email}"

    except Exception as e:
        print("❌ Email failed:", e)
        return "Email failed"


def communication_agent(state: dict):
    print("📨 Starting Communication Agent...")

    # 1. Get stakeholders
    stakeholders = get_stakeholders_from_db.invoke({})


    # 2. Send email to each
    sent_emails = []
    for person in stakeholders:
        send_email_to_stakeholder.invoke({
            "name": person["name"],
            "email": person["email"],
            "draft_text": state["draft_text"]
        })
        sent_emails.append(person["email"])

    print("✅ Emails Sent To:", sent_emails)
    return {
        **state,
        "emails_sent": sent_emails
    }



# ──────────────────────────────────────────────────────────────────────────────
# 6. LANGGRAPH PIPELINE DEFINITION
# ──────────────────────────────────────────────────────────────────────────────
def build_graph():
    g = StateGraph(dict)

    g.add_node("drafting", RunnableLambda(draft_mou))
    g.add_node("clause_retrieval", RunnableLambda(retrieve_clauses))
    g.add_node("communication", RunnableLambda(communication_agent))

    g.set_entry_point("drafting")
    g.add_edge("drafting", "clause_retrieval")
    g.add_edge("clause_retrieval", "communication")
    g.add_edge("communication", END)

    return g.compile()

