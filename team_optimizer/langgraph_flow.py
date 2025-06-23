from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_google_genai import ChatGoogleGenerativeAI

# --- ENV & DB SETUP ---
load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)

client = MongoClient("mongodb+srv://1QoSRtE75wSEibZJ:1QoSRtE75wSEibZJ@cluster0.mregq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["AgenticAI"]
draft_collection = db["MoUDrafts"]

# --- AGENT FUNCTION ---
def draft_mou(state: dict):
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

    # Save to MongoDB
    draft_collection.insert_one({
        "company_name": state["company_name"],
        "draft": draft,
        "type": state["partnership_type"]
    })

    print("✅ Draft saved to MongoDB.")
    return {
        "draft_text": draft,
        **state
    }

# --- LANGGRAPH WRAPPER ---
def build_graph():
    builder = StateGraph(dict)  # ✅ Just use dict, not custom GraphState
    builder.add_node("drafting", RunnableLambda(draft_mou))
    builder.set_entry_point("drafting")
    builder.add_edge("drafting", END)
    return builder.compile()