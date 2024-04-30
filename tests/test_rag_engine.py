"""
Unit tests for RAG engine
"""

import pytest
from rag_engine import RAGEngine
import os


class TestRAGEngine:
    """Test suite for RAG engine functionality"""
    
    @pytest.fixture
    def rag_engine(self):
        """Fixture to create RAG engine instance"""
        api_key = os.getenv("ANTHROPIC_API_KEY", "test-key")
        return RAGEngine(api_key=api_key)
    
    def test_initialization(self, rag_engine):
        """Test RAG engine initializes correctly"""
        assert rag_engine is not None
        assert rag_engine.llm is not None
        assert rag_engine.vectorstore is not None
    
    def test_retrieve_documents(self, rag_engine):
        """Test document retrieval"""
        query = "What is lateral movement?"
        documents = rag_engine.retrieve_documents(query)
        
        assert isinstance(documents, list)
        assert len(documents) > 0
        assert all(hasattr(doc, 'page_content') for doc in documents)
        assert all(hasattr(doc, 'metadata') for doc in documents)
    
    def test_format_context(self, rag_engine):
        """Test context formatting"""
        query = "MITRE ATT&CK"
        documents = rag_engine.retrieve_documents(query)
        context = rag_engine.format_context(documents)
        
        assert isinstance(context, str)
        assert len(context) > 0
        assert "[Source" in context
    
    def test_query_response_structure(self, rag_engine):
        """Test query response has correct structure"""
        query = "What is the NIST Identify function?"
        result = rag_engine.query(query)
        
        assert isinstance(result, dict)
        assert 'answer' in result
        assert 'sources' in result
        assert 'context' in result
        assert 'query' in result
        
        assert isinstance(result['answer'], str)
        assert isinstance(result['sources'], list)
        assert len(result['sources']) > 0
    
    def test_batch_query(self, rag_engine):
        """Test batch query processing"""
        queries = [
            "What is lateral movement?",
            "Explain the NIST Protect function"
        ]
        
        results = rag_engine.batch_query(queries)
        
        assert isinstance(results, list)
        assert len(results) == len(queries)
        assert all(isinstance(r, dict) for r in results)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
