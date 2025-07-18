"""
Knowledge Base Module for Smart Building AI

This module provides document processing, vector storage, and search capabilities
that can be integrated into any system.
"""

import os
import json
import hashlib
import re
import time
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
import feedparser

# Document processing imports
import PyPDF2
import docx2txt
import pandas as pd

# ChromaDB with compatibility
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: ChromaDB not available. Knowledge base will use fallback storage.")


class KnowledgeBaseManager:
    """
    Manages document storage, processing, and retrieval for the Smart Building AI
    """
    
    def __init__(self, persist_directory: str = "./knowledge_base", use_chromadb: bool = True):
        """
        Initialize the knowledge base manager
        
        Args:
            persist_directory: Directory to store the knowledge base
            use_chromadb: Whether to use ChromaDB (falls back to simple storage if False)
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        self.use_chromadb = use_chromadb and CHROMADB_AVAILABLE
        
        if self.use_chromadb:
            self._initialize_chromadb()
        else:
            self._initialize_fallback_storage()
        
        # Web scraping session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Smart Building AI Assistant/1.0 (Educational Research)'
        })
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB collection"""
        try:
            self.client = chromadb.PersistentClient(path=str(self.persist_directory))
            self.collection = self.client.get_or_create_collection(
                name="smart_building_docs"
            )
            print("✅ ChromaDB initialized successfully")
        except Exception as e:
            print(f"❌ ChromaDB initialization failed: {e}")
            self.use_chromadb = False
            self._initialize_fallback_storage()
    
    def _initialize_fallback_storage(self):
        """Initialize fallback JSON storage"""
        self.storage_file = self.persist_directory / "documents.json"
        self.documents = []
        
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
                print("✅ Fallback storage initialized successfully")
            except Exception as e:
                print(f"Warning: Could not load existing documents: {e}")
                self.documents = []
    
    def simple_embedding(self, text: str) -> List[float]:
        """Create a simple hash-based embedding for text"""
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
        words = clean_text.split()
        
        embedding = [0.0] * 100
        for word in words[:100]:
            hash_val = hash(word) % 100
            embedding[hash_val] += 1.0
        
        total = sum(embedding) or 1
        return [x / total for x in embedding]
    
    def extract_text_from_file(self, file_path: Path) -> str:
        """Extract text from various file formats"""
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension == '.pdf':
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                return text
                
            elif file_extension in ['.docx', '.doc']:
                return docx2txt.process(str(file_path))
                
            elif file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
                    
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                return df.to_string()
                
            elif file_extension == '.csv':
                df = pd.read_csv(file_path)
                return df.to_string()
                
            elif file_extension == '.json':
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    return json.dumps(data, indent=2)
                    
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"
            
        return "Unsupported file format"
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        return chunks
    
    def add_document(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a document to the knowledge base
        
        Args:
            file_path: Path to the document
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False
                
            text = self.extract_text_from_file(file_path)
            if not text or text.startswith("Error"):
                return False
                
            chunks = self.chunk_text(text)
            
            if metadata is None:
                metadata = {}
            
            base_metadata = {
                "filename": file_path.name,
                "file_path": str(file_path),
                "file_type": file_path.suffix,
                "added_date": datetime.now().isoformat(),
                **metadata
            }
            
            if self.use_chromadb:
                return self._add_to_chromadb(chunks, base_metadata, file_path.stem)
            else:
                return self._add_to_fallback(chunks, base_metadata, file_path.stem)
                
        except Exception as e:
            print(f"Error adding document: {str(e)}")
            return False
    
    def _add_to_chromadb(self, chunks: List[str], metadata: Dict[str, Any], file_stem: str) -> bool:
        """Add chunks to ChromaDB"""
        try:
            embeddings = [self.simple_embedding(chunk) for chunk in chunks]
            chunk_ids = [f"{file_stem}_{i}" for i in range(len(chunks))]
            chunk_metadata = [
                {**metadata, "chunk_index": i, "chunk_id": chunk_ids[i]}
                for i in range(len(chunks))
            ]
            
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=chunk_metadata,
                ids=chunk_ids
            )
            return True
        except Exception as e:
            print(f"Error adding to ChromaDB: {e}")
            return False
    
    def _add_to_fallback(self, chunks: List[str], metadata: Dict[str, Any], file_stem: str) -> bool:
        """Add chunks to fallback storage"""
        try:
            for i, chunk in enumerate(chunks):
                doc_entry = {
                    "id": f"{file_stem}_{i}",
                    "content": chunk,
                    "metadata": {**metadata, "chunk_index": i},
                    "embedding": self.simple_embedding(chunk)
                }
                self.documents.append(doc_entry)
            
            # Save to file
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error adding to fallback storage: {e}")
            return False
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            if self.use_chromadb:
                return self._search_chromadb(query, n_results)
            else:
                return self._search_fallback(query, n_results)
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            return []
    
    def _search_chromadb(self, query: str, n_results: int) -> List[Dict[str, Any]]:
        """Search using ChromaDB"""
        query_embedding = [self.simple_embedding(query)]
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        search_results = []
        if results['documents'][0]:
            for i in range(len(results['documents'][0])):
                search_results.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
        
        return search_results
    
    def _search_fallback(self, query: str, n_results: int) -> List[Dict[str, Any]]:
        """Search using fallback storage"""
        query_embedding = self.simple_embedding(query)
        query_words = set(query.lower().split())
        
        scored_results = []
        
        for doc in self.documents:
            # Calculate similarity score
            doc_embedding = doc.get("embedding", [])
            if doc_embedding:
                # Cosine similarity
                dot_product = sum(a * b for a, b in zip(query_embedding, doc_embedding))
                magnitude_a = sum(a * a for a in query_embedding) ** 0.5
                magnitude_b = sum(b * b for b in doc_embedding) ** 0.5
                
                if magnitude_a > 0 and magnitude_b > 0:
                    similarity = dot_product / (magnitude_a * magnitude_b)
                else:
                    similarity = 0
            else:
                similarity = 0
            
            # Text overlap score
            doc_words = set(doc["content"].lower().split())
            overlap = len(query_words.intersection(doc_words))
            text_score = overlap / len(query_words) if query_words else 0
            
            # Combined score
            final_score = (similarity * 0.7) + (text_score * 0.3)
            
            if final_score > 0:
                scored_results.append({
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "distance": 1.0 - final_score,
                    "score": final_score
                })
        
        # Sort by score and return top results
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:n_results]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            if self.use_chromadb:
                collection_info = self.collection.get()
                total_docs = len(collection_info.get('documents', []))
                
                unique_files = set()
                for metadata in collection_info.get('metadatas', []):
                    if 'filename' in metadata:
                        unique_files.add(metadata['filename'])
            else:
                total_docs = len(self.documents)
                unique_files = set()
                for doc in self.documents:
                    metadata = doc.get('metadata', {})
                    if 'filename' in metadata:
                        unique_files.add(metadata['filename'])
            
            return {
                "total_chunks": total_docs,
                "unique_files": len(unique_files),
                "files": list(unique_files),
                "storage_type": "ChromaDB" if self.use_chromadb else "Fallback JSON",
                "storage_path": str(self.persist_directory)
            }
            
        except Exception as e:
            return {
                "error": f"Error getting stats: {str(e)}",
                "storage_type": "ChromaDB" if self.use_chromadb else "Fallback JSON",
                "storage_path": str(self.persist_directory)
            }
    
    def clear_all(self):
        """Clear all documents from the knowledge base"""
        try:
            if self.use_chromadb:
                # Delete and recreate collection
                self.client.delete_collection("smart_building_docs")
                self.collection = self.client.get_or_create_collection(
                    name="smart_building_docs"
                )
            else:
                # Clear fallback storage
                self.documents = []
                with open(self.storage_file, 'w', encoding='utf-8') as f:
                    json.dump([], f)
            
            print("✅ Knowledge base cleared successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing knowledge base: {e}")
            return False


# Factory function
def create_knowledge_base(persist_directory: str = "./knowledge_base", 
                         use_chromadb: bool = True) -> KnowledgeBaseManager:
    """
    Factory function to create a knowledge base manager
    
    Args:
        persist_directory: Directory to store the knowledge base
        use_chromadb: Whether to use ChromaDB
        
    Returns:
        KnowledgeBaseManager instance
    """
    return KnowledgeBaseManager(persist_directory, use_chromadb)


# Example usage
if __name__ == "__main__":
    # Create knowledge base
    kb = create_knowledge_base()
    
    # Get stats
    stats = kb.get_stats()
    print(f"Knowledge Base Stats: {json.dumps(stats, indent=2)}")
    
    # Example search
    results = kb.search_documents("HVAC temperature control")
    print(f"Search results: {len(results)} found")
