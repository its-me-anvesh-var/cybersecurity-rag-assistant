"""
Embedding Generation Utilities
Handles text-to-vector conversion using various embedding models
"""

from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np


class EmbeddingManager:
    """Manages embedding generation and operations"""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu"
    ):
        """
        Initialize embedding manager.
        
        Args:
            model_name: HuggingFace model identifier
            device: Device to run on ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.device = device
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': device},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        print(f"Initialized embeddings with model: {model_name}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        return self.embeddings.embed_query(text)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        return self.embeddings.embed_documents(texts)
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First embedding vector
            vec2: Second embedding vector
            
        Returns:
            Similarity score (0-1, higher is more similar)
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        return float(dot_product / (norm1 * norm2))
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimensionality of embeddings.
        
        Returns:
            Embedding dimension
        """
        sample_embedding = self.embed_text("test")
        return len(sample_embedding)


# Example usage
if __name__ == "__main__":
    # Initialize
    em = EmbeddingManager()
    
    print(f"Embedding dimension: {em.get_embedding_dimension()}")
    
    # Test embeddings
    texts = [
        "What is lateral movement in cybersecurity?",
        "Explain the MITRE ATT&CK framework",
        "How to make a sandwich"
    ]
    
    print("\nGenerating embeddings...")
    embeddings = em.embed_documents(texts)
    
    print(f"Generated {len(embeddings)} embeddings")
    
    # Calculate similarities
    print("\nSimilarity scores:")
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sim = EmbeddingManager.cosine_similarity(embeddings[i], embeddings[j])
            print(f"  '{texts[i][:30]}...' <-> '{texts[j][:30]}...': {sim:.3f}")
