#langgraph_flow.py

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

from difflib import unified_diff

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import base64

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

import time

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

chroma_client = chromadb.PersistentClient(path="./clause_chromadb")
clause_collection = chroma_client.get_or_create_collection(name="clauses")

# Sentence-Transformer for embeddings
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ──────────────────────────────────────────────────────────────────────────────
# 3. AGENT 1: MoU Drafting
# ──────────────────────────────────────────────────────────────────────────────

def draft_mou(state: dict):
    print("🔁 Drafting MoU with form data:", state)


    prompt = f"""
You are a legal assistant. Create a formal Memorandum of Understanding (MoU) document.

Details:
- Company Name: {state['company_name']}
- Partnership Type: {state['partnership_type']}
- Objective: {state['objective']}
- Scope: {state['scope']}
- Date: {state['mou_date']}

Respond in professional business language. Format as an MoU.Dont reveal that it is ai generated in the content    
""" 
    response = llm.invoke(prompt)
    draft = response.content.replace("**", "").strip()

    # ✅ Generate PDF using ReportLab
    pdf_buffer = BytesIO()
    p = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    p.setFont("Helvetica", 12)

    y = height - 50  # Start from top margin

    for line in draft.split("\n"):
        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = height - 50
        p.drawString(50, y, line.strip())
        y -= 20  # Line spacing

    p.showPage()
    p.save()

    # ✅ Encode PDF to base64
    pdf_buffer.seek(0)
    pdf_bytes = pdf_buffer.getvalue()
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    # ✅ Versioning
    company_drafts = list(draft_collection.find({"company_name": state["company_name"]}))
    version = f"v{len(company_drafts) + 1}"

    # ✅ Save to MongoDB
    draft_collection.insert_one({
        "company_name": state["company_name"],
        "draft": draft,
        "type": state["partnership_type"],
        "version": version,
        "pdf_base64": pdf_base64
    })

    print("✅ Draft + PDF saved to MongoDB.")
    print("📄 Draft Text:", draft)

    return {
        **state,
        "draft_text": draft,
        "version_number": version,
        "pdf_base64": pdf_base64
    }

# ──────────────────────────────────────────────────────────────────────────────
# 4. AGENT 2: Clause Retrieval (RAG Agent)
# ──────────────────────────────────────────────────────────────────────────────

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
# 5. AGENT 3: Communication Handler Agent
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
def send_email_to_stakeholder(name: str, email: str, draft_text: str, retrieved_clauses: list) -> str:
    sender_email = "rahulsnsihub@gmail.com"
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    
    # Format clause text nicely
    clauses_str = "\n\n".join(
        [f"Clause {i+1}: {c['text']}" for i, c in enumerate(retrieved_clauses)]
    )

    # Compose the full email
    email_body = f"""
Dear {name},

Please find the initial draft of the MoU below:

{draft_text}

--- Suggested Clauses Based on Precedents ---

{clauses_str}

--- Link for the approval ---
Link : http://localhost:5173/approval

Regards,
MoU-GENIUS Agent
"""

    msg = MIMEText(email_body)
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
    retrieved_clauses = state.get("retrieved_clauses", [])

    # 1. Get stakeholders
    stakeholders = get_stakeholders_from_db.invoke({})

    # 2. Send email to each
    sent_emails = []
    for person in stakeholders:
        send_email_to_stakeholder.invoke({
            "name": person["name"],
            "email": person["email"],
            "draft_text": state["draft_text"],
            "retrieved_clauses": retrieved_clauses
        })
        sent_emails.append(person["email"])

    print("✅ Emails Sent To:", sent_emails)
    return {
        **state,
        "emails_sent": sent_emails
    }


# ──────────────────────────────────────────────────────────────────────────────
# 6. AGENT 4:  Approval Tracker Agent
# ──────────────────────────────────────────────────────────────────────────────

@csrf_exempt
def get_approvals(request):
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["AgenticAI"]
    approvals = db["approvals"]

    data = list(approvals.find({}, {"_id": 0}))  # excludes _id
    return JsonResponse({"approvals": data}, safe=False)

@csrf_exempt
def update_approval(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            status = data.get("status")

            client = MongoClient(os.getenv("MONGO_URI"))
            db = client["AgenticAI"]
            approvals = db["approvals"]

            result = approvals.update_one({"email": email}, {"$set": {"status": status}})
            if result.modified_count > 0:
                return JsonResponse({"message": "Status updated successfully"})
            else:
                return JsonResponse({"message": "No changes made"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def approval_tracker_agent(state: dict):
    print("⏳ Running Approval Tracker Agent with Idle-Watch...")

    emails_sent = state.get("emails_sent", [])
    idle_detected = True

    while idle_detected:
        approval_status = {}
        idle_detected = False  # assume all are active initially

        for email in emails_sent:
            client = MongoClient(os.getenv("MONGO_URI"))
            db = client["AgenticAI"]
            approvals = db["approvals"]

            result = approvals.find_one({"email": email}, {"_id": 0, "status": 1})
            status = result.get("status", "Pending") if result else "Pending"

            approval_status[email] = status

            if status.lower() == "idle":
                idle_detected = True

        if idle_detected:
            print("🕒 Some stakeholders still 'Idle'. Waiting for changes in DB...")
            time.sleep(5)  # ⏳ Wait for 5 seconds and recheck

    # ✅ Final pass: decide overall status
    all_approved = all(status.lower() == "approved" for status in approval_status.values())
    overall_status = "Approved" if all_approved else "Pending"

    print("✅ Approval Status:", approval_status)
    print("📝 Overall MoU Status:", overall_status)

    return {
        **state,
        "approval_status": approval_status,
        "overall_mou_status": overall_status
    }

# ──────────────────────────────────────────────────────────────────────────────
# 7. Router AGENT : Version Controller Agent
# ──────────────────────────────────────────────────────────────────────────────

def router_decision_agent(state: dict) -> str:
    print("🧭 Router Agent: Deciding next step...")
    status = state.get("overall_mou_status", "Pending").lower()

    if status == "approved":
        print("✅ MoU Approved. Proceeding to version controller.")
        return "version_controller"
    else:
        print("❌ MoU not approved. Returning to communication agent for reminder.")
        return "communication"


# ──────────────────────────────────────────────────────────────────────────────
# 8. AGENT 5: Version Controller Agent
# ──────────────────────────────────────────────────────────────────────────────

def version_controller_agent(state: dict):
    print("🧮 Running Version Controller Agent...")

    company = state.get("company_name")
    curr_text = state.get("draft_text", "")
    curr_type = state.get("partnership_type", "")

    if not company or not curr_text:
        return {**state, "version_diff": "Missing input data"}

    # Fetch all historical drafts BEFORE inserting current one
    history = list(draft_collection.find({"company_name": company}).sort("_id", 1))

    version_number = f"v{len(history) + 1}"

    if history:
        prev_doc = history[-1]  # Get the actual previous version
        prev_text = prev_doc.get("draft", "")
        prev_type = prev_doc.get("type", "")

        print(f"📜 Comparing with previous version {prev_doc.get('version', 'N/A')}...")
        print(f"Previous Type: {prev_type}, Current Type: {curr_type}")

        type_changed = curr_type != prev_type
        text_changed = curr_text != prev_text

        if not type_changed and not text_changed:
            print("⚠️ No changes from last version.")
            return {
                **state,
                "version_number": version_number,
                "version_diff": "No change from previous version."
            }

        diff_sections = []

        if type_changed:
            diff_sections.append(f"⚠️ Partnership type changed from '{prev_type}' to '{curr_type}'")

        if text_changed:
            diff = list(unified_diff(
                prev_text.splitlines(),
                curr_text.splitlines(),
                fromfile='Previous Draft',
                tofile='Current Draft',
                lineterm=''
            ))
            diff_sections.append("\n".join(diff))

        diff_text = "\n\n".join(diff_sections)

    else:
        print("📘 First version, no diff to compare.")
        diff_text = "Initial version created."

    # 🔁 Save *after* comparison
    draft_collection.insert_one({
        "company_name": company,
        "draft": curr_text,
        "version": version_number,
        "type": curr_type
    })
    print(f"✅ Saved {version_number} to database.")

    return {
        **state,
        "version_number": version_number,
        "version_diff": diff_text
    }



# ──────────────────────────────────────────────────────────────────────────────
# 9. LANGGRAPH PIPELINE DEFINITION
# ──────────────────────────────────────────────────────────────────────────────

def build_graph():
    g = StateGraph(dict)

    g.add_node("drafting", RunnableLambda(draft_mou))
    g.add_node("clause_retrieval", RunnableLambda(retrieve_clauses))
    g.add_node("communication", RunnableLambda(communication_agent))
    g.add_node("approval_tracker", RunnableLambda(approval_tracker_agent))
    g.add_node("version_controller", RunnableLambda(version_controller_agent)) 

    g.set_entry_point("drafting")
    g.add_edge("drafting", "clause_retrieval")
    g.add_edge("clause_retrieval", "communication")
    g.add_edge("communication", "approval_tracker")
    # 🔥 Conditional routing (no router node needed now)
    g.add_conditional_edges(
        "approval_tracker",
        router_decision_agent,  # directly use function
        path_map={
            "version_controller": "version_controller",
            "communication": "communication"
        }
    )
    g.add_edge("version_controller", END)  

    return g.compile()

