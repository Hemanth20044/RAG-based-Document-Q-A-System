# 🧠 DocMind — RAG-based Document Q&A System

Ask questions to any PDF or Word document and get answers with exact source citations — powered by LangChain, FAISS, and Groq LLaMA 3.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38-red)
![LangChain](https://img.shields.io/badge/LangChain-0.2-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Live Demo
> _Add your Streamlit Cloud URL here after deployment_

---

## 📸 Features

- 📄 Upload **PDF** or **DOCX** files
- 💬 Ask natural language questions
- 📎 Get answers with **exact source citations** (page numbers + text snippets)
- 🧠 **Conversational memory** — ask follow-up questions
- ⚡ Super fast responses via **Groq + LLaMA 3**
- 🔒 100% free — no OpenAI costs

---

## 🛠️ Tech Stack

| Component | Tool |
|---|---|
| LLM | Groq API (LLaMA 3 8B) — Free |
| Embeddings | HuggingFace sentence-transformers — Free, local |
| Vector Store | FAISS — Free, local |
| RAG Framework | LangChain |
| UI | Streamlit |

---

## ⚙️ How It Works

```
PDF/DOCX Upload
      ↓
Extract Text (PyPDF / python-docx)
      ↓
Split into chunks (RecursiveCharacterTextSplitter)
      ↓
Convert chunks to embeddings (sentence-transformers)
      ↓
Store in FAISS vector database
      ↓
User asks a question
      ↓
Question → embedding → similarity search → top 4 chunks
      ↓
Chunks + question → Groq LLaMA 3
      ↓
Answer + Source Citations
```

---

## 🏃 Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/Hemanth20044/RAG-based-Document-Q-A-System.git
cd rag-doc-qa
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get free Groq API key
- Go to https://console.groq.com
- Sign up → Create API Key → Copy it

### 5. Create `.env` file
```bash
cp .env.example .env
# Open .env and paste your Groq API key
```

### 6. Run the app
```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser 🎉

---

## ☁️ Deploy Free on Streamlit Cloud

1. Push this repo to GitHub
2. Go to https://share.streamlit.io
3. Connect your GitHub repo
4. Add secret: `GROQ_API_KEY = your_key_here`
5. Click Deploy!

---

## 📁 Project Structure

```
rag-doc-qa/
├── app.py              # Streamlit UI
├── rag_engine.py       # Core RAG logic
├── requirements.txt    # Dependencies
├── .env.example        # API key template
├── .gitignore          # Keeps .env safe
└── README.md
```

---

## 💼 Resume Description

```
RAG-based Document Q&A System                               [https://github.com/Hemanth20044]
• Built a production-style retrieval-augmented generation (RAG) pipeline
  using LangChain, FAISS vector store, and Groq LLM (LLaMA 3)
• Implemented semantic text chunking, local embeddings via
  sentence-transformers, and multi-turn conversational memory
• Deployed on Streamlit Cloud with source citation and live chat interface
Tech: Python · LangChain · FAISS · HuggingFace · Groq API · Streamlit
```

---

## 🙋 Author

Built by [KURETI HEMANTH KUMAR] · [https://www.linkedin.com/in/hemanthkureti/] · [(https://hemanthk.me/)]
