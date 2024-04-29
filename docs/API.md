# API Documentation

## RAGEngine Class

Core RAG implementation for querying the knowledge base.

### Initialization

```python
from rag_engine import RAGEngine

rag = RAGEngine(
    api_key="your_anthropic_api_key",  # Optional, reads from .env
    model_name="claude-3-5-sonnet-20241022",
    temperature=0.3,
    top_k=5,
    persist_directory="./vectorstore"
)
```

**Parameters:**
- `api_key` (str, optional): Anthropic API key
- `model_name` (str): Claude model identifier
- `temperature` (float): LLM temperature (0-1)
- `top_k` (int): Number of documents to retrieve
- `persist_directory` (str): ChromaDB storage path

### Methods

#### query(question: str) -> Dict

Main query interface.

```python
result = rag.query("What is lateral movement in MITRE ATT&CK?")

print(result['answer'])
print(result['sources'])
```

**Returns:**
```python
{
    'answer': str,        # Generated response
    'sources': [          # Source documents
        {
            'source': str,    # Document name
            'chunk': str      # Content preview
        },
        ...
    ],
    'context': str,       # Retrieved context (debugging)
    'query': str          # Original question
}
```

#### batch_query(questions: List[str]) -> List[Dict]

Process multiple queries.

```python
questions = [
    "What is the NIST Identify function?",
    "Explain CIS Control 1"
]

results = rag.batch_query(questions)
```

## DocumentIngestor Class

Handles document loading and embedding.

### Initialization

```python
from ingest_documents import DocumentIngestor

ingestor = DocumentIngestor(
    data_dir="./data/raw",
    persist_directory="./vectorstore",
    chunk_size=1000,
    chunk_overlap=200
)
```

### Methods

#### ingest()

Run full ingestion pipeline.

```python
ingestor.ingest()
```

Performs:
1. Load documents from data_dir
2. Chunk documents
3. Generate embeddings
4. Store in ChromaDB

## Utility Classes

### DocumentLoader

```python
from utils.document_loader import DocumentLoader

loader = DocumentLoader()

# Load single file
docs = loader.load_pdf(Path("doc.pdf"))

# Load directory
docs = loader.load_directory(
    Path("./data/raw"),
    extensions=['.pdf', '.txt', '.md']
)
```

### TextSplitter

```python
from utils.text_splitter import TextSplitter

splitter = TextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)
```

### EmbeddingManager

```python
from utils.embeddings import EmbeddingManager

em = EmbeddingManager()

# Single text
embedding = em.embed_text("What is cybersecurity?")

# Multiple texts
embeddings = em.embed_documents([
    "Text 1",
    "Text 2"
])

# Similarity
sim = EmbeddingManager.cosine_similarity(emb1, emb2)
```

## Examples

### Basic Query

```python
from rag_engine import RAGEngine

rag = RAGEngine()
result = rag.query("What is credential dumping?")

print("Answer:", result['answer'])
print("\nSources:")
for source in result['sources']:
    print(f"- {source['source']}")
```

### Custom Configuration

```python
rag = RAGEngine(
    temperature=0.5,  # More creative
    top_k=10          # Retrieve more documents
)

result = rag.query("Compare NIST and CIS frameworks")
```

### Batch Processing

```python
questions = [
    "What is phishing?",
    "What is ransomware?",
    "What is DDoS?"
]

results = rag.batch_query(questions)

for q, r in zip(questions, results):
    print(f"Q: {q}")
    print(f"A: {r['answer'][:100]}...")
    print()
```
