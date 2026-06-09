import streamlit as st
from rag_engine import load_document, build_vectorstore, build_qa_chain, ask_question

# ── Page Config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="DocMind — AI Document Q&A",
    page_icon="🧠",
    layout="wide"
)

# ── Custom CSS for clean look ─────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        color: #e8e8f0;
    }
    [data-testid="stSidebar"] {
        background: rgba(255,255,255,0.04);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        margin-bottom: 8px;
        padding: 4px;
    }
    [data-testid="stChatInput"] textarea {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(99,102,241,0.4) !important;
        border-radius: 12px !important;
        color: #e8e8f0 !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(99,102,241,0.4);
    }
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.03);
        border: 1px dashed rgba(99,102,241,0.5);
        border-radius: 12px;
        padding: 8px;
    }
    .streamlit-expanderHeader {
        background: rgba(99,102,241,0.1) !important;
        border-radius: 8px !important;
        color: #a5b4fc !important;
    }
    .stSuccess {
        background: rgba(34,197,94,0.1) !important;
        border: 1px solid rgba(34,197,94,0.3) !important;
        border-radius: 8px !important;
    }
    .stInfo {
        background: rgba(99,102,241,0.1) !important;
        border: 1px solid rgba(99,102,241,0.3) !important;
        border-radius: 8px !important;
    }
    h1 {
        background: linear-gradient(135deg, #6366f1, #a78bfa, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
    }
    .stSpinner { color: #6366f1 !important; }
    .source-card {
        background: rgba(99,102,241,0.08);
        border: 1px solid rgba(99,102,241,0.2);
        border-left: 3px solid #6366f1;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 6px 0;
        font-size: 0.85rem;
        color: #c4b5fd;
    }
    hr { border-color: rgba(255,255,255,0.08) !important; }
    .stat-box {
        background: rgba(99,102,241,0.1);
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 10px;
        padding: 12px 16px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────
st.title("🧠 DocMind")
st.caption("Upload any PDF or Word document · Ask anything · Get answers with source citations")
st.divider()

# ── Session State Init ────────────────────────────────────────────
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "doc_name" not in st.session_state:
    st.session_state.doc_name = None
if "question_count" not in st.session_state:
    st.session_state.question_count = 0

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📄 Upload Your Document")
    st.caption("Supported: PDF, DOCX")

    uploaded_file = st.file_uploader(
        "Drop your file here",
        type=["pdf", "docx"],
        label_visibility="collapsed"
    )

    if uploaded_file and uploaded_file.name != st.session_state.doc_name:
        with st.spinner("🔄 Reading & indexing document..."):
            try:
                docs = load_document(uploaded_file)
                vectorstore = build_vectorstore(docs)
                st.session_state.qa_chain = build_qa_chain(vectorstore)
                st.session_state.doc_name = uploaded_file.name
                st.session_state.chat_history = []
                st.session_state.question_count = 0
                st.success(f"✅ Document ready!")
            except Exception as e:
                import traceback
                traceback.print_exc()
                st.error(f"❌ Error: {str(e)}")

    if st.session_state.doc_name:
        st.markdown("---")
        st.markdown("**📂 Active Document:**")
        st.info(f"📝 {st.session_state.doc_name}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='stat-box'>
                <div style='font-size:1.4rem;font-weight:700;color:#a78bfa'>
                    {st.session_state.question_count}
                </div>
                <div style='font-size:0.7rem;color:#94a3b8'>Questions</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='stat-box'>
                <div style='font-size:1.4rem;font-weight:700;color:#38bdf8'>
                    {len(st.session_state.chat_history) // 2}
                </div>
                <div style='font-size:0.7rem;color:#94a3b8'>Exchanges</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")
        if st.button("🗑️ Clear & Upload New"):
            st.session_state.qa_chain = None
            st.session_state.chat_history = []
            st.session_state.doc_name = None
            st.session_state.question_count = 0
            st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ How It Works")
    steps = [
        ("1️⃣", "Upload your PDF or DOCX"),
        ("2️⃣", "Text is split into smart chunks"),
        ("3️⃣", "Each chunk is turned into numbers (embeddings)"),
        ("4️⃣", "Your question finds the most relevant chunks"),
        ("5️⃣", "Groq LLaMA 3 answers using only those chunks"),
        ("6️⃣", "You get the answer + exact source pages"),
    ]
    for icon, step in steps:
        st.markdown(f"{icon} {step}")

    st.markdown("---")
    st.markdown("### 🛠️ Tech Stack")
    st.markdown("""
    - 🦜 **LangChain** — RAG pipeline
    - 🗄️ **FAISS** — Vector search
    - 🤗 **HuggingFace** — Embeddings
    - ⚡ **Groq + LLaMA 3** — LLM
    - 🎈 **Streamlit** — UI
    """)

# ── Main Area ─────────────────────────────────────────────────────
if not st.session_state.qa_chain:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding: 60px 20px;'>
            <div style='font-size: 5rem; margin-bottom: 20px;'>📄</div>
            <h2 style='color: #a78bfa; font-size: 1.5rem;'>
                Upload a document to get started
            </h2>
            <p style='color: #64748b; font-size: 1rem; margin-top: 10px;'>
                Upload any PDF or Word document from the sidebar.<br>
                Then ask questions — and get answers with exact source citations.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**💡 Example questions you can ask:**")
        example_qs = [
            "📌 Summarize this document in 5 bullet points",
            "🔍 What are the main findings?",
            "📊 What data or statistics are mentioned?",
            "❓ What problem is this document solving?",
            "📝 What are the key recommendations?",
        ]
        for q in example_qs:
            st.markdown(f"> {q}")
    st.stop()

# ── Chat History Display ──────────────────────────────────────────
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant" and message.get("sources"):
            with st.expander(f"📎 View {len(message['sources'])} Source(s)"):
                for i, src in enumerate(message["sources"], 1):
                    page = src.get("page", "N/A")
                    page_label = f"Page {int(page) + 1}" if str(page).isdigit() else f"Section {i}"
                    st.markdown(f"""
                    <div class='source-card'>
                        <strong>📍 Source {i} — {page_label}</strong><br>
                        <span style='color:#e2e8f0;'>{src.get('snippet', '')}...</span>
                    </div>
                    """, unsafe_allow_html=True)

# ── Chat Input ────────────────────────────────────────────────────
if question := st.chat_input("Ask anything about your document..."):

    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching document & generating answer..."):
            try:
                answer, sources = ask_question(st.session_state.qa_chain, question)
                st.session_state.question_count += 1
            except Exception as e:
                import traceback
                traceback.print_exc()
                answer = f"❌ Something went wrong: {str(e)}"
                sources = []

        st.markdown(answer)

        if sources:
            with st.expander(f"📎 View {len(sources)} Source(s)"):
                for i, src in enumerate(sources, 1):
                    page = src.get("page", "N/A")
                    page_label = f"Page {int(page) + 1}" if str(page).isdigit() else f"Section {i}"
                    st.markdown(f"""
                    <div class='source-card'>
                        <strong>📍 Source {i} — {page_label}</strong><br>
                        <span style='color:#e2e8f0;'>{src.get('snippet', '')}...</span>
                    </div>
                    """, unsafe_allow_html=True)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })