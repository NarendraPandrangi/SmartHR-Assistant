import os
import requests
import numpy as np
import uuid
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configuration details
KRUTRIM_API_KEY = os.environ.get("KRUTRIM_API_KEY", "6CIYq3OVlXswA9FW4eME6Hqv")
KRUTRIM_API_URL = "https://cloud.olakrutrim.com/v1/chat/completions"

# Memory Stores
vectorizer = TfidfVectorizer(stop_words='english')
documents_store = {} 
texts_corpus = []
current_id = 0

from typing import Optional

def add_document_to_store(content: str, metadata: Optional[dict] = None):
    global current_id, texts_corpus
    chunks = [c for c in content.split('\n\n') if c.strip()]
    added_ids = []
    
    for chunk in chunks:
        doc_uuid = str(uuid.uuid4())
        documents_store[current_id] = {"content": chunk, "metadata": metadata, "id": doc_uuid}
        texts_corpus.append(chunk)
        added_ids.append(doc_uuid)
        current_id += 1
        
    return added_ids

def retrieve_context(query: str, top_k: int = 3):
    if len(texts_corpus) == 0:
        return []
    
    try:
        tfidf_matrix = vectorizer.fit_transform(texts_corpus)
        query_vec = vectorizer.transform([query])
        sims = cosine_similarity(query_vec, tfidf_matrix).flatten()
        
        # Sort indices descending
        best_indices = sims.argsort()[::-1]
        
        retrieved_texts = []
        for idx in best_indices:
            if len(retrieved_texts) >= top_k: break
            if sims[idx] > 0.05 and idx in documents_store:
                retrieved_texts.append(documents_store[idx]["content"])
        
        return retrieved_texts
    except Exception as e:
        print(f"Retrieval Error: {e}")
        return []

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
