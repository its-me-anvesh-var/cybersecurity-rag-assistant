"""
Unit tests for embedding utilities
"""

import pytest
from utils.embeddings import EmbeddingManager


class TestEmbeddingManager:
    """Test suite for embedding functionality"""
    
    @pytest.fixture
    def embedding_manager(self):
        """Fixture to create embedding manager instance"""
        return EmbeddingManager()
    
    def test_initialization(self, embedding_manager):
        """Test embedding manager initializes correctly"""
        assert embedding_manager is not None
        assert embedding_manager.embeddings is not None
        assert embedding_manager.model_name == "sentence-transformers/all-MiniLM-L6-v2"
    
    def test_embedding_dimension(self, embedding_manager):
        """Test embedding dimension is correct"""
        dim = embedding_manager.get_embedding_dimension()
        assert dim == 384  # all-MiniLM-L6-v2 produces 384-dimensional vectors
    
    def test_embed_single_text(self, embedding_manager):
        """Test embedding a single text"""
        text = "What is cybersecurity?"
        embedding = embedding_manager.embed_text(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)
    
    def test_embed_multiple_texts(self, embedding_manager):
        """Test embedding multiple texts"""
        texts = [
            "MITRE ATT&CK framework",
            "NIST Cybersecurity Framework",
            "CIS Controls"
        ]
        embeddings = embedding_manager.embed_documents(texts)
        
        assert isinstance(embeddings, list)
        assert len(embeddings) == len(texts)
        assert all(len(emb) == 384 for emb in embeddings)
    
    def test_cosine_similarity(self, embedding_manager):
        """Test cosine similarity calculation"""
        text1 = "cybersecurity threat detection"
        text2 = "detecting security threats"
        text3 = "cooking recipes"
        
        emb1 = embedding_manager.embed_text(text1)
        emb2 = embedding_manager.embed_text(text2)
        emb3 = embedding_manager.embed_text(text3)
        
        # Similar texts should have higher similarity
        sim_similar = EmbeddingManager.cosine_similarity(emb1, emb2)
        sim_different = EmbeddingManager.cosine_similarity(emb1, emb3)
        
        assert sim_similar > sim_different
        assert 0 <= sim_similar <= 1
        assert 0 <= sim_different <= 1


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
