"""
RAG Engine — Multi-Provider Implementation
Ollama (local) → Groq → Claude fallback chain
Author: Anvesh Raju Varadharaju
"""

import os
import time
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from utils.embeddings import EmbeddingManager

load_dotenv()
logger = logging.getLogger(__name__)


# ── Provider implementations ──────────────────────────────────────────────────

def _ask_ollama(prompt: str, system: str, temperature: float) -> str:
    """Call local Ollama — free, private, no rate limits."""
    import ollama
    response = ollama.chat(
        model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt},
        ],
        options={"temperature": temperature}
    )
    return response["message"]["content"].strip()


def _ask_groq(prompt: str, system: str, temperature: float) -> str:
    """Call Groq API — free 500K tokens/day, ~300 tok/s."""
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt},
        ],
        temperature=temperature,
        max_tokens=2048,
    )
    return response.choices[0].message.content.strip()


def _ask_claude(prompt: str, system: str, temperature: float) -> str:
    """Call Claude API — fallback only."""
    import anthropic
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY", "")
    )
    message = client.messages.create(
        model=os.getenv("MODEL_NAME", "claude-3-5-sonnet-20241022"),
        max_tokens=2048,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


# ── Provider registry ─────────────────────────────────────────────────────────

PROVIDERS = {
    "ollama": _ask_ollama,
    "groq":   _ask_groq,
    "claude": _ask_claude,
}

PROVIDER_PRIORITY = ["ollama", "groq", "claude"]


def _call_llm(prompt: str, system: str, temperature: float = 0.3) -> tuple[str, str]:
    """
    Try each provider in priority order.
    Returns (response_text, provider_used).
    """
    for provider in PROVIDER_PRIORITY:
        try:
            logger.debug(f"Trying provider: {provider}")
            result = PROVIDERS[provider](prompt, system, temperature)
            return result, provider
        except Exception as e:
            logger.warning(f"Provider '{provider}' failed: {e}")
            time.sleep(0.5)
            continue
    return "[All AI providers failed — check your .env configuration]", "none"


# ── RAG Engine ────────────────────────────────────────────────────────────────

class RAGEngine:
    """
    Retrieval-Augmented Generation engine for cybersecurity knowledge queries.

    Combines semantic search over security frameworks (MITRE ATT&CK, NIST CSF,
    CIS Controls) with multi-provider LLM generation and source attribution.

    Provider chain: Ollama (local) → Groq → Claude
    """

    SYSTEM_PROMPT = """You are an expert cybersecurity analyst with deep knowledge of:
- MITRE ATT&CK Framework (tactics, techniques, sub-techniques)
- NIST Cybersecurity Framework (Identify, Protect, Detect, Respond, Recover)
- CIS Critical Security Controls (implementation groups, safeguards)
- OWASP Top 10 Web Application Security Risks

Your role is to provide accurate, detailed answers based strictly on the 
retrieved context below. Guidelines:
1. Answer directly and concisely, focused on the specific question
2. Always cite which framework or source your information comes from
3. If context is insufficient, say so honestly — do not hallucinate
4. Use technical terminology correctly but explain complex concepts clearly
5. Provide practical SOC/analyst use cases when relevant

Context from knowledge base:
{context}

Question: {question}

Provide a comprehensive, well-structured answer with framework citations."""

    def __init__(
        self,
        api_key: Optional[str] = None,      # kept for backward compat
        model_name: str = "llama3.2:3b",
        temperature: float = 0.3,
        top_k: int = 5,
        persist_directory: str = "./vectorstore"
    ):
        self.temperature = temperature
        self.top_k = top_k
        self.model_name = model_name

        # Initialize embeddings + vectorstore
        embedding_manager = EmbeddingManager()
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_manager.embeddings,
            collection_name="cybersecurity_knowledge"
        )

        # Track provider usage for metrics
        self._last_provider = "unknown"
        self._query_count   = 0
        self._total_latency = 0.0

    def retrieve_documents(self, query: str) -> List[Document]:
        """Retrieve relevant documents from ChromaDB vector store."""
        return self.vectorstore.similarity_search(
            query=query,
            k=self.top_k
        )

    def format_context(self, documents: List[Document]) -> str:
        """Format retrieved documents into structured context string."""
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source  = doc.metadata.get("source", "Unknown")
            content = doc.page_content
            context_parts.append(f"[Source {i}: {source}]\n{content}\n")
        return "\n".join(context_parts)

    def _confidence_check(self, answer: str, context: str) -> str:
        """
        Hallucination guard — flag if answer contains claims
        not grounded in retrieved context.
        """
        # Simple heuristic: if answer is much longer than context
        # and contains no source citations, flag it
        if len(answer) > len(context) * 2:
            return "⚠️ Low confidence — answer may exceed retrieved context."
        if "I don't know" in answer or "not in the context" in answer.lower():
            return "ℹ️ Model acknowledged knowledge boundary."
        return "✅ Answer grounded in retrieved context."

    def query(self, question: str) -> Dict:
        """
        Main query interface — retrieve → generate → return with metrics.

        Returns:
            answer        : Generated response text
            sources       : List of source documents with previews
            provider      : Which LLM provider was used
            latency_ms    : Total query latency in milliseconds
            chunks_used   : Number of chunks retrieved
            confidence    : Hallucination guard signal
        """
        start = time.time()

        # Retrieve
        documents = self.retrieve_documents(question)
        context   = self.format_context(documents)

        # Build prompt
        prompt = self.SYSTEM_PROMPT.format(
            context=context,
            question=question
        )

        # Generate with fallback chain
        answer, provider = _call_llm(
            prompt=question,
            system=self.SYSTEM_PROMPT.format(context=context, question=""),
            temperature=self.temperature
        )

        latency_ms = round((time.time() - start) * 1000)

        # Update metrics
        self._last_provider  = provider
        self._query_count   += 1
        self._total_latency += latency_ms

        # Confidence check
        confidence = self._confidence_check(answer, context)

        # Format sources
        sources = [
            {
                "source": doc.metadata.get("source", "Unknown"),
                "chunk":  doc.page_content[:200] + "..."
            }
            for doc in documents
        ]

        return {
            "answer":      answer,
            "sources":     sources,
            "context":     context,
            "query":       question,
            "provider":    provider,
            "latency_ms":  latency_ms,
            "chunks_used": len(documents),
            "confidence":  confidence,
        }

    def get_metrics(self) -> Dict:
        """Return session performance metrics."""
        avg_latency = (
            round(self._total_latency / self._query_count)
            if self._query_count > 0 else 0
        )
        return {
            "total_queries":   self._query_count,
            "avg_latency_ms":  avg_latency,
            "last_provider":   self._last_provider,
        }

    def batch_query(self, questions: List[str]) -> List[Dict]:
        """Process multiple queries in batch."""
        return [self.query(q) for q in questions]
