"""
Document Loader Utilities
Handles loading different document formats (PDF, TXT, MD)
"""

from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader


class DocumentLoader:
    """Unified document loader for multiple file formats"""
    
    @staticmethod
    def load_pdf(file_path: Path) -> List[Document]:
        """
        Load PDF document.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of Document objects with page content and metadata
        """
        loader = PyPDFLoader(str(file_path))
        docs = loader.load()
        
        # Add source metadata
        for doc in docs:
            doc.metadata['source'] = file_path.name
            doc.metadata['type'] = 'pdf'
            doc.metadata['file_path'] = str(file_path)
        
        return docs
    
    @staticmethod
    def load_text(file_path: Path) -> List[Document]:
        """
        Load text document (.txt, .md).
        
        Args:
            file_path: Path to text file
            
        Returns:
            List of Document objects
        """
        loader = TextLoader(str(file_path), encoding='utf-8')
        docs = loader.load()
        
        for doc in docs:
            doc.metadata['source'] = file_path.name
            doc.metadata['type'] = 'text'
            doc.metadata['file_path'] = str(file_path)
        
        return docs
    
    @staticmethod
    def load_directory(directory: Path, extensions: List[str] = None) -> List[Document]:
        """
        Load all documents from a directory.
        
        Args:
            directory: Path to directory
            extensions: List of file extensions to load (e.g., ['.pdf', '.txt'])
                       If None, loads all supported formats
            
        Returns:
            List of all loaded documents
        """
        if extensions is None:
            extensions = ['.pdf', '.txt', '.md']
        
        all_docs = []
        
        for ext in extensions:
            for file_path in directory.glob(f"*{ext}"):
                print(f"Loading {file_path.name}...")
                
                if ext == '.pdf':
                    docs = DocumentLoader.load_pdf(file_path)
                else:
                    docs = DocumentLoader.load_text(file_path)
                
                all_docs.extend(docs)
        
        print(f"Total documents loaded: {len(all_docs)}")
        return all_docs


# Example usage
if __name__ == "__main__":
    loader = DocumentLoader()
    
    # Test loading
    data_dir = Path("../data/raw")
    if data_dir.exists():
        docs = loader.load_directory(data_dir)
        print(f"\nLoaded {len(docs)} documents")
        
        if docs:
            print(f"\nSample document:")
            print(f"Source: {docs[0].metadata['source']}")
            print(f"Content preview: {docs[0].page_content[:200]}...")
