import os
import traceback
import tempfile

# Try to import heavy dependencies; if unavailable, fall back to lightweight stubs
USE_STUB = False
try:
    from dotenv import load_dotenv
    from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_groq import ChatGroq
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory

    load_dotenv()

    # ── Embeddings ────────────────────────────────────────────────────
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True, "batch_size": 32}
    )

    # ── LLM via Groq ──────────────────────────────────────────────────
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.2
    )

except Exception:
    # If any heavy import fails, use stubs so the app can run for development/UI testing
    USE_STUB = True


def load_document(uploaded_file):
    suffix = ".pdf" if uploaded_file.name.endswith(".pdf") else ".docx"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    if suffix == ".docx":
        loader = Docx2txtLoader(tmp_path)
        documents = loader.load()
    else:
        # Try normal text extraction first
        import fitz  # pymupdf
        documents = []
        pdf = fitz.open(tmp_path)
        
        for page_num, page in enumerate(pdf):
            text = page.get_text()
            
            # If no text, use OCR
            if not text.strip():
                import pytesseract
                from PIL import Image
                pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
                pix = page.get_pixmap(dpi=400)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img)
            
            if text.strip():
                from langchain_core.documents import Document
                documents.append(Document(
                    page_content=text,
                    metadata={"page": page_num, "source": uploaded_file.name}
                ))
        
        pdf.close()

    os.unlink(tmp_path)
    print(f"Loaded {len(documents)} pages")
    print(f"First page text: '{documents[0].page_content[:200] if documents else ''}'")
    return documents


def build_vectorstore(documents):
    """Builds a vectorstore; stubbed version uses simple token overlap ranking."""
    if not USE_STUB:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(chunks, embeddings)
        return vectorstore

    # Stub vectorstore: list of chunks (dicts) we can search by naive overlap
    chunks = []
    for i, doc in enumerate(documents):
        text = doc.get("page_content") if isinstance(doc, dict) else getattr(doc, "page_content", str(doc))
        chunks.append({"id": i, "text": text, "metadata": {"page": doc.get("metadata", {}).get("page", i) if isinstance(doc, dict) else {}}})

    class StubVectorStore:
        def __init__(self, chunks):
            self.chunks = chunks

        def as_retriever(self, search_type="similarity", search_kwargs=None):
            k = (search_kwargs or {}).get("k", 4)

            def retrieve(query):
                q_words = set(query.lower().split())
                scored = []
                for c in self.chunks:
                    c_words = set(c["text"].lower().split())
                    # simple Jaccard similarity
                    inter = len(q_words & c_words)
                    union = len(q_words | c_words) or 1
                    score = inter / union
                    scored.append((score, c))
                scored.sort(key=lambda x: x[0], reverse=True)
                return [s[1] for s in scored[:k]]

            return retrieve

    return StubVectorStore(chunks)


def build_qa_chain(vectorstore):
    if not USE_STUB:
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )

        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )

        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            verbose=False
        )
        return chain

    # Stub chain: simple object with invoke method
    class StubChain:
        def __init__(self, retriever):
            self.retriever = retriever

        def invoke(self, payload):
            q = payload.get("question", "")
            retrieved = self.retriever(q) if callable(self.retriever) else []
            # Build a simple answer string and include retrieved chunks as sources
            answer = f"[Stub answer] I found {len(retrieved)} relevant chunk(s). Ask with real deps for better answers."
            source_documents = []
            for r in retrieved:
                # normalize to expected interface
                source_documents.append(type("D", (), {"metadata": r.get("metadata", {}), "page_content": r.get("text", "")})())
            return {"answer": answer, "source_documents": source_documents}

    # For stub, vectorstore may be a StubVectorStore instance; its as_retriever returns a callable
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4}) if hasattr(vectorstore, "as_retriever") else (lambda q: [])
    return StubChain(retriever)


def ask_question(chain, question):
    try:
        response = chain.invoke({"question": question})
    except Exception as e:
        traceback.print_exc()
        raise e

    answer = response.get("answer", "Sorry, I couldn't generate an answer.")
    sources = response.get("source_documents", [])

    source_info = []
    seen = set()
    for doc in sources:
        try:
            # handle both stub and real doc interfaces
            meta = getattr(doc, "metadata", {}) if not isinstance(doc, dict) else doc.get("metadata", {})
            page = meta.get("page", "N/A")
            content = getattr(doc, "page_content", None) or (doc.get("page_content") if isinstance(doc, dict) else str(doc))
            snippet = content[:200].strip()
            key = (str(page), snippet[:50])
            if key not in seen:
                seen.add(key)
                source_info.append({"page": page, "snippet": snippet})
        except Exception:
            continue

    return answer, source_info