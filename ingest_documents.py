"""
Document Ingestion - Process and embed security framework documents
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from utils.document_loader import DocumentLoader
from utils.text_splitter import TextSplitter
from utils.embeddings import EmbeddingManager

load_dotenv()


class DocumentIngestor:
    """
    Handles loading, chunking, and embedding of security framework documents.
    """
    
    def __init__(
        self,
        data_dir: str = "./data/raw",
        persist_directory: str = "./vectorstore",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize document ingestor.
        
        Args:
            data_dir: Directory containing raw documents
            persist_directory: ChromaDB persistence path
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.data_dir = Path(data_dir)
        self.persist_directory = persist_directory
        
        # Initialize components
        self.document_loader = DocumentLoader()
        self.text_splitter = TextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.embedding_manager = EmbeddingManager()
        
        self.documents = []
    
    def _create_sample_documents(self):
        """Create sample cybersecurity documents for demo purposes."""
        
        # MITRE ATT&CK sample
        mitre_content = """# MITRE ATT&CK Framework Overview

MITRE ATT&CK is a globally-accessible knowledge base of adversary tactics, techniques, and procedures (TTPs) based on real-world observations.

## Tactics

**Initial Access**: The adversary is trying to get into your network.
Techniques include phishing, exploit public-facing applications, valid accounts, supply chain compromise.

**Execution**: The adversary is trying to run malicious code.
Techniques include command and scripting interpreters, user execution, scheduled tasks.

**Persistence**: The adversary is trying to maintain their foothold.
Techniques include boot or logon autostart execution, create or modify system process, scheduled tasks.

**Privilege Escalation**: The adversary is trying to gain higher-level permissions.
Techniques include abuse elevation control mechanism, access token manipulation, process injection.

**Defense Evasion**: The adversary is trying to avoid being detected.
Techniques include obfuscated files or information, process injection, masquerading.

**Credential Access**: The adversary is trying to steal account names and passwords.
Techniques include credential dumping, brute force, input capture.

**Discovery**: The adversary is trying to figure out your environment.
Techniques include account discovery, network service scanning, system information discovery.

**Lateral Movement**: The adversary is trying to move through your environment.
Techniques include remote services, use alternate authentication material, internal spearphishing.

**Collection**: The adversary is trying to gather data of interest.
Techniques include data from information repositories, input capture, screen capture.

**Command and Control (C2)**: The adversary is trying to communicate with compromised systems.
Techniques include application layer protocol, encrypted channel, web service.

**Exfiltration**: The adversary is trying to steal data.
Techniques include exfiltration over C2 channel, automated exfiltration, scheduled transfer.

**Impact**: The adversary is trying to manipulate, interrupt, or destroy systems and data.
Techniques include data destruction, defacement, disk wipe, resource hijacking.
"""
        
        # NIST CSF sample
        nist_content = """# NIST Cybersecurity Framework

The NIST Cybersecurity Framework provides a policy framework of computer security guidance for organizations.

## Core Functions

**Identify (ID)**: Develop organizational understanding to manage cybersecurity risk.
- Asset Management (ID.AM)
- Business Environment (ID.BE)
- Governance (ID.GV)
- Risk Assessment (ID.RA)
- Risk Management Strategy (ID.RM)
- Supply Chain Risk Management (ID.SC)

**Protect (PR)**: Develop and implement appropriate safeguards.
- Identity Management and Access Control (PR.AC)
- Awareness and Training (PR.AT)
- Data Security (PR.DS)
- Information Protection Processes (PR.IP)
- Maintenance (PR.MA)
- Protective Technology (PR.PT)

**Detect (DE)**: Develop and implement activities to identify cybersecurity events.
- Anomalies and Events (DE.AE)
- Security Continuous Monitoring (DE.CM)
- Detection Processes (DE.DP)

**Respond (RS)**: Develop and implement activities to take action regarding detected cybersecurity incidents.
- Response Planning (RS.RP)
- Communications (RS.CO)
- Analysis (RS.AN)
- Mitigation (RS.MI)
- Improvements (RS.IM)

**Recover (RC)**: Develop and implement activities to maintain resilience.
- Recovery Planning (RC.RP)
- Improvements (RC.IM)
- Communications (RC.CO)
"""
        
        # CIS Controls sample
        cis_content = """# CIS Critical Security Controls

The CIS Controls are a prioritized set of actions to protect organizations from cyber attack vectors.

## Implementation Groups

**IG1 (Basic Cyber Hygiene)**: Essential cyber hygiene for all organizations
**IG2 (Enterprise Security)**: Builds on IG1 for organizations with dedicated cybersecurity staff
**IG3 (Sensitive Data Protection)**: For organizations protecting highly sensitive data

## Top 18 Controls

**Control 1: Inventory and Control of Enterprise Assets**
Actively manage (inventory, track, correct) all enterprise assets connected to the infrastructure.

**Control 2: Inventory and Control of Software Assets**
Actively manage (inventory, track, correct) all software on the network so unauthorized software is found and prevented.

**Control 3: Data Protection**
Develop processes to identify, classify, securely handle, retain, and dispose of data.

**Control 4: Secure Configuration**
Establish and maintain secure configurations for hardware, software, and network devices.

**Control 5: Account Management**
Use processes and tools to assign administrative privileges and track access to systems.

**Control 6: Access Control Management**
Use processes and tools to track access to enterprise assets and user actions.

**Control 7: Continuous Vulnerability Management**
Develop a plan to assess and remediate weaknesses continuously.

**Control 8: Audit Log Management**
Collect, alert, review, and retain audit logs of security-relevant events.

**Control 9: Email and Web Browser Protections**
Improve defenses and capabilities to identify and block threats coming through email and web browsers.

**Control 10: Malware Defenses**
Prevent or control installation, spread, and execution of malicious applications and code.

**Control 11: Data Recovery**
Establish and maintain data recovery practices to ensure data availability.

**Control 12: Network Infrastructure Management**
Establish, implement, and manage enterprise devices and software in network infrastructure.

**Control 13: Network Monitoring and Defense**
Operate processes and tooling to establish and maintain comprehensive network monitoring.

**Control 14: Security Awareness and Skills Training**
Establish security awareness program for all staff and specialized training for specific roles.

**Control 15: Service Provider Management**
Develop process to evaluate service providers who hold sensitive data or responsibility for assets.

**Control 16: Application Software Security**
Manage the security life cycle of in-house developed, hosted, or acquired software.

**Control 17: Incident Response Management**
Establish processes to develop and maintain incident response capabilities.

**Control 18: Penetration Testing**
Test the effectiveness of defenses by simulating attacks.
"""
        
        # Write sample documents
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "mitre_attack.txt").write_text(mitre_content)
        (self.data_dir / "nist_csf.txt").write_text(nist_content)
        (self.data_dir / "cis_controls.txt").write_text(cis_content)
        
        print("Sample documents created in data/raw/")
    
    def load_documents(self) -> List[Document]:
        """
        Load all documents from data directory.
        
        Supports: .pdf, .txt, .md files
        """
        # Check if data directory exists
        if not self.data_dir.exists() or not list(self.data_dir.glob("*")):
            print(f"No documents found. Creating sample documents...")
            self._create_sample_documents()
        
        # Load all documents
        all_docs = self.document_loader.load_directory(
            self.data_dir,
            extensions=['.pdf', '.txt', '.md']
        )
        
        return all_docs
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        chunks = self.text_splitter.split_documents(documents)
        
        # Print statistics
        stats = TextSplitter.get_chunk_statistics(chunks)
        print(f"\nChunk Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        return chunks
    
    def create_vectorstore(self, chunks: List[Document]):
        """
        Create and persist vector store from document chunks.
        """
        print("\nCreating vector embeddings...")
        
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embedding_manager.embeddings,
            persist_directory=self.persist_directory,
            collection_name="cybersecurity_knowledge"
        )
        
        print(f"Vector store created and persisted to {self.persist_directory}")
        return vectorstore
    
    def ingest(self):
        """
        Main ingestion pipeline: load -> chunk -> embed -> persist.
        """
        print("Starting document ingestion pipeline...\n")
        
        # Load documents
        documents = self.load_documents()
        
        if not documents:
            print("No documents found. Exiting.")
            return
        
        # Chunk documents
        chunks = self.chunk_documents(documents)
        
        # Create vector store
        self.create_vectorstore(chunks)
        
        print("\n✅ Ingestion complete!")


# CLI entry point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest cybersecurity documents")
    parser.add_argument(
        "--data-dir",
        type=str,
        default="./data/raw",
        help="Directory containing raw documents"
    )
    parser.add_argument(
        "--persist-dir",
        type=str,
        default="./vectorstore",
        help="ChromaDB persistence directory"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Size of text chunks"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Overlap between chunks"
    )
    
    args = parser.parse_args()
    
    ingestor = DocumentIngestor(
        data_dir=args.data_dir,
        persist_directory=args.persist_dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
    
    ingestor.ingest()
