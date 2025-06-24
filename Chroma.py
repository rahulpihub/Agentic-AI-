import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings

# Step 1: Load CSV
df = pd.read_csv("clauses.csv")  # columns: clause_id, clause_type, partnership_type, text

# Step 2: Initialize ChromaDB Client
chroma_client = chromadb.PersistentClient(path="./clause_chromadb")
collection = chroma_client.get_or_create_collection(name="clauses")

# Step 3: Embed and Store
embedder = SentenceTransformer("all-MiniLM-L6-v2")

for index, row in df.iterrows():
    embedding = embedder.encode(row["text"]).tolist()
    collection.add(
        documents=[row["text"]],
        ids=[str(row["clause_id"])],
        metadatas=[{
            "clause_type": row["clause_type"],
            "partnership_type": row["partnership_type"]
        }],
        embeddings=[embedding]
    )

print("✅ Clauses inserted into ChromaDB.")

# # test_chroma.py

# from sentence_transformers import SentenceTransformer
# import chromadb

# # 1. Point at the exact same folder you used for ingestion
# chroma_client = chromadb.PersistentClient(path="./clause_chromadb")
# collection = chroma_client.get_or_create_collection(name="clauses")

# # 2. Load the same embedder you used for ingestion
# embedder = SentenceTransformer("all-MiniLM-L6-v2")

# # 3. Test query
# test_queries = [
#     "Interns confidentiality obligations",
#     "How can the internship be terminated?",
#     "Governing law for the agreement"
# ]

# for q in test_queries:
#     emb = embedder.encode(q).tolist()
#     results = collection.query(query_embeddings=[emb], n_results=3)
#     print(f"\nQuery: {q}")
#     for doc in results["documents"][0]:
#         print(" -", doc)
