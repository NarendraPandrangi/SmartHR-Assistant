# Dynamic Knowledge Retrieval Chatbot (RAG)

This project implements **Problem Statement 6: Dynamic Knowledge Retrieval Chatbot (RAG)**. It is a full-stack Retrieval-Augmented Generation (RAG) application that allows users to upload documents dynamically and interact with a chatbot that retrieves context-aware answers natively from the uploaded content.

## 🚀 Key Features
- **Retrieval Pipeline**: A robust ingestion engine that extracts text from `.txt` and `.pdf` files, segments them into chunks, bounds them to high-dimensional embeddings, and stores them in a lightning-fast vector array.
- **Context-Based Answer Generation**: Queries are instantly paired with identical context chunks via cosine similarity scoring before being passed to the Krutrim LLM API for accurate reasoning.
- **Smart Fallbacks**: The framework handles unknown queries gracefully by politely denying answers when insufficient context is supplied—preventing standard LLM hallucination issues.
- **Dynamic Source Uploading**: Upload custom documents natively through the chat interface UI! 
- **Secure Authentication**: Built-in Email/Password and Google OAuth functionality powered entirely by Firebase. 

## 🛠️ Technology Stack
- **Frontend**: HTML5, Vanilla JavaScript, CSS (Premium Glassmorphism Aesthetic)
- **Authentication**: Firebase Authentication (Compat SDK)
- **Backend API**: Python, FastAPI, Uvicorn
- **AI / Embeddings**: `sentence-transformers` (all-MiniLM-L6-v2), PyPDF2, Krutrim LLM

## ⚙️ How to Set Up the Project

### 1. Configure Firebase Credentials
Open `frontend/app.js` and locate the `firebaseConfig` object at the top of the file. Ensure that it correctly matches your Firebase Project settings containing your unique `apiKey` and `projectId`. Note that **Google Sign-In** must also be manually enabled in your Firebase Console Authentication settings.

### 2. Install Python Dependencies
Ensure you have Python 3.10+ installed. Navigate to the backend directory and install all requirements from the command line:

```powershell
cd backend
pip install -r requirements.txt
```

*(Note: We use a lightweight numpy implementation for the vector indexing arrays instead of `faiss-cpu` to prevent extreme local disk/disk-space overhead issues).*

### 3. Start the Backend API Server
Launch the FastAPI development server:
```powershell
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
The backend includes a hardcoded Krutrim API key. You can update this default key anytime inside `backend/rag_engine.py`.

### 4. Start the Frontend Local Server
To properly authenticate with Google, Firebase requires the frontend web pages to be served over a localhost protocol rather than double-clicking a raw file path. Open a second terminal:
```powershell
cd frontend
python -m http.server 3000
```

### 5. Chat Setup
Visit `http://localhost:3000/index.html` in your web browser. 
Create an account or login. Inside the chat interface, click **Upload Knowledge** to establish your first knowledge source (e.g., `hr_policy.pdf`), and then start asking questions!
