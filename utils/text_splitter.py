"""
Text Splitting Utilities
Implements various chunking strategies for document processing
"""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class TextSplitter:
    """Handles document chunking with various strategies"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None
    ):
        """
        Initialize text splitter.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of overlapping characters between chunks
            separators: List of separators to use (hierarchical)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if separators is None:
            # Default hierarchical separators
            separators = ["\n\n", "\n", ". ", " ", ""]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=separators
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.
        
        Args:
            documents: List of Document objects to split
            
        Returns:
            List of chunked Document objects with preserved metadata
        """
        chunks = self.splitter.split_documents(documents)
        
        # Add chunk metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata['chunk_id'] = i
            chunk.metadata['chunk_size'] = len(chunk.page_content)
        
        print(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks
    
    def split_text(self, text: str, metadata: dict = None) -> List[Document]:
        """
        Split raw text into chunks.
        
        Args:
            text: Raw text to split
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of Document objects
        """
        chunks = self.splitter.split_text(text)
        
        documents = []
        for i, chunk in enumerate(chunks):
            doc_metadata = metadata.copy() if metadata else {}
            doc_metadata['chunk_id'] = i
            doc_metadata['chunk_size'] = len(chunk)
            
            documents.append(Document(
                page_content=chunk,
                metadata=doc_metadata
            ))
        
        return documents
    
    @staticmethod
    def get_chunk_statistics(chunks: List[Document]) -> dict:
        """
        Calculate statistics about chunks.
        
        Args:
            chunks: List of chunked documents
            
        Returns:
            Dictionary with statistics
        """
        sizes = [len(chunk.page_content) for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'avg_chunk_size': sum(sizes) / len(sizes) if sizes else 0,
            'min_chunk_size': min(sizes) if sizes else 0,
            'max_chunk_size': max(sizes) if sizes else 0,
            'total_characters': sum(sizes)
        }


# Example usage
if __name__ == "__main__":
    # Sample text
    sample_text = """
    MITRE ATT&CK is a globally-accessible knowledge base of adversary tactics and techniques 
    based on real-world observations. The ATT&CK knowledge base is used as a foundation for the 
    development of specific threat models and methodologies in the private sector, in government, 
    and in the cybersecurity product and service community.
    
    The tactics represent the "why" of an ATT&CK technique or sub-technique. It is the adversary's 
    tactical goal: the reason for performing an action. For example, an adversary may want to achieve 
    credential access.
    """ * 10  # Repeat to make it longer
    
    # Initialize splitter
    splitter = TextSplitter(chunk_size=200, chunk_overlap=50)
    
    # Split text
    chunks = splitter.split_text(sample_text, metadata={'source': 'sample.txt'})
    
    print(f"Created {len(chunks)} chunks")
    print(f"\nChunk statistics:")
    stats = TextSplitter.get_chunk_statistics(chunks)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\nFirst chunk:")
    print(chunks[0].page_content)
