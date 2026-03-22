from fastapi import FastAPI, HTTPException, Request, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import rag_engine

app = FastAPI(title="RAG Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import Optional

class QueryRequest(BaseModel):
    query: str

class DocRequest(BaseModel):
    content: str
    metadata: Optional[dict] = None

@app.post("/api/add_document")
def add_document(req: DocRequest):
    try:
        doc_id = rag_engine.add_document_to_store(req.content, req.metadata)
        return {"message": "Document successfully added to vector store.", "doc_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text_content = ""
        if file.filename.lower().endswith(".pdf"):
            import PyPDF2
            import io
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content += extracted + "\n\n"
        else:
            text_content = content.decode("utf-8", errors="ignore")
            
        text_content = text_content.strip()
        if not text_content:
            raise Exception("No readable text could be extracted from this file. (If this is a PDF, it may be a scanned image or locked).")
            
        doc_ids = rag_engine.add_document_to_store(text_content, {"filename": file.filename})
        
        if not doc_ids:
            raise Exception("File didn't contain enough valid text paragraphs to index.")
            
        return {"message": "File successfully uploaded and indexed.", "doc_ids": doc_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@app.post("/api/chat")
def chat(req: QueryRequest):
    try:
        context_texts = rag_engine.retrieve_context(req.query)
        answer = rag_engine.generate_answer(req.query, context_texts)
        return {
            "answer": answer,
            "context_used": context_texts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
