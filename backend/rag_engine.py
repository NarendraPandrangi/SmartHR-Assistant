import os
import requests
from sentence_transformers import SentenceTransformer
import numpy as np
import uuid

# Configuration details
KRUTRIM_API_KEY = os.environ.get("KRUTRIM_API_KEY", "6CIYq3OVlXswA9FW4eME6Hqv")
KRUTRIM_API_URL = "https://cloud.olakrutrim.com/v1/chat/completions"

# Initialize embedding model
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding_dim = embedding_model.get_sentence_embedding_dimension()
except Exception as e:
    print(f"Error loading model: {e}")
    embedding_dim = 384 # Default for all-MiniLM-L6-v2

# In-memory numpy List
embeddings_store = []
documents_store = {} 
current_id = 0

from typing import Optional

def add_document_to_store(content: str, metadata: Optional[dict] = None):
    global current_id
    chunks = [c for c in content.split('\n\n') if c.strip()]
    added_ids = []
    
    for chunk in chunks:
        vector = embedding_model.encode([chunk])[0]
        # L2 normalize
        norm = np.linalg.norm(vector)
        v = vector / norm if norm > 0 else vector
        embeddings_store.append(v)
        
        doc_uuid = str(uuid.uuid4())
        documents_store[current_id] = {"content": chunk, "metadata": metadata, "id": doc_uuid}
        added_ids.append(doc_uuid)
        current_id += 1
        
    return added_ids

def retrieve_context(query: str, top_k: int = 3):
    if len(embeddings_store) == 0:
        return []
    
    query_vector = embedding_model.encode([query])[0]
    norm = np.linalg.norm(query_vector)
    v = query_vector / norm if norm > 0 else query_vector
    
    similarities = []
    for idx, emb in enumerate(embeddings_store):
        sim = np.dot(v, emb)
        similarities.append((sim, idx))
        
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    k = min(top_k, len(embeddings_store))
    top_results = similarities[:k]
    
    retrieved_texts = []
    for sim, idx in top_results:
        if sim > 0.15 and idx in documents_store:
            retrieved_texts.append(documents_store[idx]["content"])
                
    return retrieved_texts

def generate_answer(query: str, context_texts: list):
    if not context_texts:
        return "I'm sorry, I couldn't find any relevant information regarding that query in the provided documents."
        
    system_prompt = (
        "You are an intelligent knowledge base chatbot. "
        "Answer the user's query using STRICTLY the provided context below, but sound natural. "
        "DO NOT start your response with phrases like 'Based on the given context' or 'According to the context'. Provide the answer directly. "
        "If you do not know the answer based on the context, politely state that you do not have enough information.\n\n"
        "Context:\n"
        + "\n---\n".join(context_texts)
    )
    
    headers = {
        "Authorization": f"Bearer {KRUTRIM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "Krutrim-spectre-v2",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        "temperature": 0.3
    }
    
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.post(KRUTRIM_API_URL, json=payload, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error calling Krutrim API: {e}")
        return f"(API Call Failed. Mock Response) Based on context: {context_texts[0][:150]}..."

# Initial seeding of data
add_document_to_store(
    "Work From Home Policy: Employees are allowed to work from home up to 2 days a week with prior manager approval.",
    {"type": "policy"}
)
add_document_to_store(
    "Leave Policy: You get 20 days of paid leave annually. Sick leaves require a medical certificate if taking 3 or more consecutive days.",
    {"type": "policy"}
)
add_document_to_store(
    "Working Hours: The official standard working hours are from 9:00 AM to 6:00 PM, Monday to Friday.",
    {"type": "faq"}
)
