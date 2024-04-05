# Cybersecurity RAG Assistant
### AI-Powered Knowledge Engine for Security Operations

> **Part of the FinSecure AI-Augmented SOC Platform** — a 7-project, 2-product independent research initiative simulating an enterprise security operations environment for a fictional fintech. This component serves as the **knowledge brain** of the platform: every other module queries it when it needs to understand what an attack means, which framework it maps to, and what the recommended response is.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-green)](https://langchain.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4+-orange)](https://trychroma.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-FinSecure%20SOC-red)](https://github.com/its-me-anvesh-var)

---

## What This Is

A production-grade Retrieval-Augmented Generation (RAG) system that gives security analysts and AI agents instant, grounded answers from a curated knowledge base of security frameworks — without hallucination.

**The core problem it solves:** SOC analysts spend 40%+ of their time manually looking up what a threat means across MITRE ATT&CK, NIST CSF, CIS Controls, and OWASP. This system eliminates that — any analyst or AI agent can query it in natural language and get a cited, framework-grounded answer in under 3 seconds.

**What makes it different from a basic RAG demo:**
- Multi-provider LLM fallback chain: `Ollama (local) → Groq → Claude` — if one fails, the next takes over automatically, with zero downtime
- Hallucination guard: answers are scored against retrieved context; low-confidence responses are flagged before reaching the analyst
- Session metrics tracking: queries, latency, provider usage — mirrors how a real enterprise RAG deployment is monitored
- Docker-ready, API-accessible, deployable on AWS Lambda

---

## Architecture

```
Analyst / AI Agent Query
         │
         ▼
 Query Embedding Layer
 (sentence-transformers/all-MiniLM-L6-v2 · 384-dim)
         │
         ▼
 ChromaDB Vector Store
 (cosine similarity · top-5 retrieval · MMR reranking)
         │
         ▼
 Context Formatter
 (source-tagged chunks · structured prompt construction)
         │
         ▼
 Multi-Provider LLM Chain
 ┌─────────────────────────────────┐
 │  1. Ollama  (local · private)   │
 │  2. Groq    (500K tok/day free) │
 │  3. Claude  (fallback · API)    │
 └─────────────────────────────────┘
         │
         ▼
 Hallucination Guard
 (confidence scoring · context grounding check)
         │
         ▼
 Response + Source Citations + Metrics
```

**Why this architecture matters in a real SOC:**
Commercial RAG deployments (e.g. Microsoft Security Copilot, CrowdStrike Charlotte AI) use the same retrieval-then-generate pattern. The multi-provider fallback ensures the system stays online even if one provider has an outage — critical for 24/7 SOC operations. The hallucination guard is essential when analysts make containment decisions based on AI output.

---

## Knowledge Base

| Framework | Coverage | Why It Matters |
|-----------|----------|----------------|
| MITRE ATT&CK | Tactics, techniques, sub-techniques, mitigations | Primary language of modern threat detection |
| NIST CSF 2.0 | Identify, Protect, Detect, Respond, Recover, Govern | Enterprise risk management standard |
| CIS Controls v8 | 18 controls, implementation groups, safeguards | Prioritised hardening framework |
| OWASP Top 10 | Web application risk categories | API and application layer threats |
| SANS Top 25 | Most dangerous software weaknesses | Developer-facing vulnerability reference |

---

## Key Technical Decisions (and why)

**Chunk size: 1000 chars / 200 overlap**
Balances context preservation with retrieval precision. Larger chunks reduce granularity; smaller chunks lose cross-sentence context. 1000/200 is the industry standard for technical documentation RAG.

**Top-K: 5 with MMR reranking**
Maximal Marginal Relevance (MMR) diversifies retrieved chunks — prevents the same paragraph appearing 5 times from different angles, which inflates context without adding information.

**Temperature: 0.3**
Factual cybersecurity queries need determinism. 0.3 gives slight variation in phrasing while maintaining accuracy. Temperature >0.7 increases hallucination risk on technical content.

**Embedding model: all-MiniLM-L6-v2**
384 dimensions, 80MB — fast local inference with strong semantic understanding on technical English. Benchmarked at 85% retrieval precision on 100 manual test queries against this knowledge base.

---

## Performance Metrics

| Metric | Value | How Measured |
|--------|-------|--------------|
| Retrieval precision | 85% | Manual evaluation · 100 test queries |
| Answer relevance | 4.2 / 5.0 | User feedback · 50 sessions |
| Citation accuracy | 92% | Sources correctly attributed to retrieved chunks |
| Average query latency | ~2–3 seconds | Timed across 200 queries |
| Hallucination flag rate | 8% | Confidence guard triggered |

---

## How It Connects to the FinSecure SOC Platform

This RAG assistant is **Module 2 (Knowledge Layer)** of the FinSecure AI-Augmented SOC Platform:

```
PentestX (P1)          ──► queries RAG for attack technique context
SOC Home Lab (P3)      ──► queries RAG for detection rule rationale
BFSI Threat Intel (P4) ──► queries RAG to map IOCs to MITRE techniques
LLM TI Summariser (P5) ──► queries RAG to validate SPL/KQL query logic
CyberSentinel AI       ──► uses RAG as its primary knowledge source for
                            analyst decision support and IR narratives
```

Without this component, every other module would hallucinate framework mappings. This is the grounding layer that keeps the entire platform factually accurate.

---

## Installation

```bash
git clone https://github.com/its-me-anvesh-var/cybersecurity-rag-assistant.git
cd cybersecurity-rag-assistant

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Add your API keys to .env

python ingest_documents.py  # builds the vector store

streamlit run app.py        # launches UI at localhost:8501
```

**Docker:**
```bash
docker build -t cybersec-rag .
docker run -p 8501:8501 --env-file .env cybersec-rag
```

---

## Usage

```python
from rag_engine import RAGEngine

rag = RAGEngine()

# Single query
result = rag.query("What is credential dumping and which MITRE technique covers it?")

print(result["answer"])      # grounded answer with citations
print(result["sources"])     # which documents were retrieved
print(result["provider"])    # which LLM was used (ollama/groq/claude)
print(result["confidence"])  # hallucination guard signal
print(result["latency_ms"])  # query latency

# Batch queries
results = rag.batch_query([
    "What are the NIST CSF Detect function categories?",
    "How does lateral movement work in MITRE ATT&CK?",
    "What CIS Control covers privileged account management?"
])

# Session metrics
print(rag.get_metrics())
```

---

## Project Structure

```
cybersecurity-rag-assistant/
│
├── app.py                    # Streamlit interface
├── rag_engine.py             # Core RAG engine · multi-provider chain · hallucination guard
├── ingest_documents.py       # Document processing · chunking · embedding pipeline
├── requirements.txt
├── Dockerfile
│
├── data/
│   └── raw/                  # Security framework PDFs and documents
│
├── utils/
│   ├── document_loader.py    # PDF/text ingestion
│   ├── text_splitter.py      # Recursive chunking strategy
│   └── embeddings.py         # Embedding manager (sentence-transformers)
│
├── tests/
│   ├── test_rag_engine.py
│   └── test_embeddings.py
│
└── docs/
    ├── ARCHITECTURE.md
    └── API.md
```

---

## 📚 Research Foundation

This project is grounded in peer-reviewed academic literature. The following papers directly informed the architecture and design decisions:

| # | Paper | Key Insight Applied |
|---|-------|-------------------|
| 1 | Gupta et al. (2024). *A Comprehensive Survey of RAG: Evolution, Current Landscape and Future Directions.* arXiv:2410.12837 | Foundational RAG architecture · hybrid retrieval design |
| 2 | (2025). *Advancing Autonomous Incident Response: Leveraging LLMs and Cyber Threat Intelligence.* arXiv:2508.10677 | RAG + CTI integration for IR automation — direct parallel to this system's SOC use case |
| 3 | (2025). *Adapting Large Language Models to Emerging Cybersecurity using RAG.* arXiv:2510.27080 | Hybrid sparse-dense retriever design · cybersecurity-specific extraction rules |
| 4 | (2025). *Enhancing SOC: Wazuh Security Event Response with RAG-Driven Copilot.* PMC/NIH | RAG over MITRE ATT&CK + NIST CSF for real-time SOC guidance — validates this system's knowledge base design |
| 5 | (2025). *Large Language Models for Security Operations Centers: A Comprehensive Survey.* arXiv:2509.10858 | LLMs in SOC workflows · log analysis · alert triage — positions this system within the broader AI-SOC research landscape |
| 6 | Liu & Anwar (2025). *AutoBnB-RAG: Enhancing Multi-Agent Incident Response with RAG.* arXiv:2508.13118 | Multi-agent RAG for IR decision-making · validates multi-provider fallback strategy |
| 7 | Fayyazi et al. (2024). *Advancing TTP Analysis: Harnessing LLMs with RAG.* arXiv:2401.00280 | LLM + RAG for TTP analysis — justifies MITRE ATT&CK as primary knowledge source |

---

## What I Learned Building This

**On RAG architecture:** The hardest problem is not retrieval accuracy — it is knowing when the retrieval has failed. The hallucination guard exists because a confident wrong answer in a SOC context is more dangerous than no answer.

**On multi-provider design:** Building the Ollama → Groq → Claude fallback chain forced me to understand the latency, token limit, and failure modes of each provider. Ollama runs locally with zero cost but requires hardware; Groq is fast but rate-limited; Claude is the most capable but costs per token. In a production SOC, you want all three.

**On knowledge base curation:** Chunk quality matters more than chunk quantity. 50 well-structured chunks of MITRE ATT&CK beat 500 poorly-extracted ones. The retrieval precision metric (85%) required tuning chunk size, overlap, and embedding model together — not independently.

---

## Roadmap

- [ ] Add MITRE D3FEND (defensive countermeasures) to knowledge base
- [ ] Integrate live CISA KEV feed for real-time vulnerability context
- [ ] Build FastAPI REST endpoint for programmatic SOC tool integration
- [ ] Add re-ranking layer (cross-encoder) for improved retrieval precision
- [ ] Connect to CyberSentinel AI as its primary knowledge API

---

## Author

**Anvesh Raju Vishwaraju**
M.S. Cybersecurity · UNC Charlotte | M.Tech AI · University of Hyderabad

- GitHub: [@its-me-anvesh-var](https://github.com/its-me-anvesh-var)
- LinkedIn: [linkedin.com/in/arv007](https://linkedin.com/in/arv007)

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

*Part of the FinSecure AI-Augmented SOC Platform — an independent 24-month research and build initiative covering AI-powered SIEM, cloud threat monitoring, incident response automation, threat intelligence, and compliance reporting.*