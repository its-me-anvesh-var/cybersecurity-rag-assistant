"""
Cybersecurity RAG Assistant — Streamlit UI
Multi-provider: Ollama (local) → Groq → Claude
Author: Anvesh Raju Varadharaju
"""

import json
import time
import streamlit as st
from datetime import datetime
from pathlib import Path
from rag_engine import RAGEngine
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cybersecurity RAG Assistant",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 0.95rem;
    }
    .answer-box {
        background-color: #f8f9ff;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 4px solid #4361ee;
        margin: 1rem 0;
    }
    .metric-card {
        background: #f0f4ff;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        text-align: center;
        border: 1px solid #d0d8ff;
    }
    .provider-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .confidence-ok  { color: #2d6a4f; background: #d8f3dc; padding: 3px 10px; border-radius: 10px; }
    .confidence-warn { color: #7d4f00; background: #fff3cd; padding: 3px 10px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "rag_engine" not in st.session_state:
    with st.spinner("Loading knowledge base and AI engine..."):
        try:
            st.session_state.rag_engine = RAGEngine()
            st.success("✅ Ready — using Ollama (local) with Groq fallback")
        except Exception as e:
            st.error(f"Failed to initialise RAG engine: {e}")
            st.info("Make sure Ollama is running: `ollama serve`")
            st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "feedback" not in st.session_state:
    st.session_state.feedback = {}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-header">🔐 Cybersecurity RAG Assistant</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Semantic search over MITRE ATT&CK · NIST CSF · CIS Controls · OWASP | '
    'Ollama (local) → Groq → Claude</p>',
    unsafe_allow_html=True
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📚 Knowledge Base")
    st.markdown("""
    - **MITRE ATT&CK** — Tactics, techniques, sub-techniques
    - **NIST CSF** — Identify, Protect, Detect, Respond, Recover
    - **CIS Controls** — 18 critical security controls
    - **OWASP Top 10** — Web application security risks
    """)

    st.header("⚙️ Settings")
    top_k = st.slider("Chunks retrieved", 1, 10, 5,
                      help="More chunks = more context but slower")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3,
                            help="Lower = more deterministic answers")

    st.header("🤖 AI Provider Chain")
    st.markdown("""
    ```
    1. Ollama  (local, free, private)
    2. Groq    (free 500K tokens/day)
    3. Claude  (fallback)
    ```
    """)

    st.header("📊 Session Metrics")
    metrics = st.session_state.rag_engine.get_metrics()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Queries", metrics["total_queries"])
    with col2:
        st.metric("Avg latency", f"{metrics['avg_latency_ms']}ms")
    st.caption(f"Last provider: `{metrics['last_provider']}`")

    st.header("💡 Example Queries")
    examples = [
        "What is lateral movement in MITRE ATT&CK?",
        "Explain the NIST Identify function",
        "What CIS Controls cover endpoint security?",
        "How does credential dumping work?",
        "What is Kerberoasting and how do I detect it?",
        "Explain OWASP SQL injection prevention",
    ]
    for q in examples:
        if st.button(q, key=f"ex_{q}"):
            st.session_state.current_query = q
            st.rerun()

    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.session_state.feedback = {}
        st.rerun()

    # Export chat history
    if st.session_state.chat_history:
        export_data = [
            {"query": q, "answer": r["answer"], "provider": r.get("provider",""),
             "latency_ms": r.get("latency_ms", 0)}
            for q, r in st.session_state.chat_history
        ]
        st.download_button(
            "📥 Export Chat (JSON)",
            data=json.dumps(export_data, indent=2),
            file_name=f"rag_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# ── Chat history display ──────────────────────────────────────────────────────
for i, (query, response) in enumerate(st.session_state.chat_history):
    with st.container():
        st.markdown(f"**🧑 You:** {query}")

        # Answer box
        st.markdown(
            f'<div class="answer-box">🤖 <strong>Assistant:</strong><br><br>'
            f'{response["answer"]}</div>',
            unsafe_allow_html=True
        )

        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.caption(f"⚡ {response.get('latency_ms', '—')} ms")
        with col2:
            st.caption(f"📄 {response.get('chunks_used', '—')} chunks")
        with col3:
            st.caption(f"🤖 {response.get('provider', '—')}")
        with col4:
            conf = response.get("confidence", "")
            if "✅" in conf:
                st.caption("✅ Grounded")
            elif "⚠️" in conf:
                st.caption("⚠️ Low confidence")
            else:
                st.caption("ℹ️ Info")

        # Feedback buttons
        fb_key = f"feedback_{i}"
        if fb_key not in st.session_state.feedback:
            col_up, col_down, col_space = st.columns([1, 1, 8])
            with col_up:
                if st.button("👍", key=f"up_{i}"):
                    st.session_state.feedback[fb_key] = "positive"
                    st.rerun()
            with col_down:
                if st.button("👎", key=f"down_{i}"):
                    st.session_state.feedback[fb_key] = "negative"
                    st.rerun()
        else:
            fb = st.session_state.feedback[fb_key]
            st.caption(f"Feedback: {'👍 Helpful' if fb == 'positive' else '👎 Not helpful'}")

        # Sources
        with st.expander("📄 View Retrieved Sources"):
            for j, source in enumerate(response.get("sources", []), 1):
                st.markdown(f"**Source {j}:** `{source['source']}`")
                st.text(source["chunk"])

        st.markdown("---")

# ── Query input ───────────────────────────────────────────────────────────────
st.header("💬 Ask a Question")

query = st.text_input(
    "Cybersecurity question:",
    value=st.session_state.get("current_query", ""),
    placeholder="e.g., What Splunk query detects Kerberoasting?",
    key="query_input"
)

if "current_query" in st.session_state:
    del st.session_state.current_query

col1, col2 = st.columns([6, 1])
with col1:
    submit = st.button("🔍 Ask", type="primary", use_container_width=True)
with col2:
    if st.button("🔄 Reset"):
        st.rerun()

# ── Process query ─────────────────────────────────────────────────────────────
if submit and query:
    with st.spinner("Searching knowledge base and generating answer..."):
        try:
            st.session_state.rag_engine.top_k = top_k
            st.session_state.rag_engine.temperature = temperature

            response = st.session_state.rag_engine.query(query)
            st.session_state.chat_history.append((query, response))
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {e}")
            with st.expander("Error Details"):
                st.exception(e)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.85rem;'>"
    "Built by <strong>Anvesh Raju Varadharaju</strong> | "
    "<a href='https://github.com/its-me-anvesh-var/cybersecurity-rag-assistant'>GitHub</a> | "
    "<a href='https://linkedin.com/in/anvesh-raju-v'>LinkedIn</a><br>"
    "LangChain · ChromaDB · Ollama · Groq · MITRE ATT&CK · NIST CSF · CIS Controls"
    "</div>",
    unsafe_allow_html=True
)
