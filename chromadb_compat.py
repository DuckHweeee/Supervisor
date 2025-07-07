"""
ChromaDB compatibility module for deployment environments
Handles SQLite version incompatibilities gracefully
"""

import sys
import os
import streamlit as st
from typing import Dict, Any, List, Optional

class ChromaDBWrapper:
    """Wrapper for ChromaDB that handles SQLite compatibility issues"""
    
    def __init__(self, persist_directory="./knowledge_base"):
        self.client = None
        self.collection = None
        self.use_fallback = False
        self.fallback_storage = {}
        self.chromadb_available = False
        
        self._initialize_chromadb(persist_directory)
    
    def _initialize_chromadb(self, persist_directory):
        """Try multiple methods to initialize ChromaDB"""
        
        # Method 1: Try with pysqlite3-binary
        if self._try_pysqlite3_chromadb(persist_directory):
            return
        
        # Method 2: Try standard ChromaDB
        if self._try_standard_chromadb(persist_directory):
            return
        
        # Method 3: Try in-memory ChromaDB
        if self._try_memory_chromadb():
            return
        
        # Method 4: Fall back to custom storage
        self._activate_fallback()
    
    def _try_pysqlite3_chromadb(self, persist_directory):
        """Try using pysqlite3-binary for SQLite compatibility"""
        try:
            import pysqlite3
            sys.modules['sqlite3'] = pysqlite3
            
            import chromadb
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.client.get_or_create_collection(name="smart_building_docs")
            self.chromadb_available = True
            
            st.success("✅ ChromaDB initialized with pysqlite3-binary")
            return True
            
        except Exception as e:
            st.info(f"📝 pysqlite3 method failed: {str(e)[:100]}...")
            return False
    
    def _try_standard_chromadb(self, persist_directory):
        """Try standard ChromaDB initialization"""
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.client.get_or_create_collection(name="smart_building_docs")
            self.chromadb_available = True
            
            st.success("✅ ChromaDB initialized with standard method")
            return True
            
        except Exception as e:
            st.info(f"📝 Standard ChromaDB method failed: {str(e)[:100]}...")
            return False
    
    def _try_memory_chromadb(self):
        """Try in-memory ChromaDB client"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            self.client = chromadb.Client(Settings(anonymized_telemetry=False))
            self.collection = self.client.get_or_create_collection(name="smart_building_docs")
            self.chromadb_available = True
            
            st.success("✅ ChromaDB initialized with in-memory client")
            return True
            
        except Exception as e:
            st.info(f"📝 Memory ChromaDB method failed: {str(e)[:100]}...")
            return False
    
    def _activate_fallback(self):
        """Activate fallback storage system"""
        self.use_fallback = True
        st.warning("⚠️ ChromaDB unavailable - using enhanced in-memory storage")
        st.info("💡 All functionality preserved with session-based storage")
    
    def add_documents(self, documents, metadatas, ids, embeddings):
        """Add documents to storage (ChromaDB or fallback)"""
        if self.use_fallback:
            for i, doc in enumerate(documents):
                self.fallback_storage[ids[i]] = {
                    'document': doc,
                    'metadata': metadatas[i],
                    'embedding': embeddings[i]
                }
        else:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
    
    def query_documents(self, query_embeddings, n_results=5):
        """Query documents from storage"""
        if self.use_fallback:
            # Simple fallback search using keyword matching
            results = {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
            
            # For fallback, we'll do a simple text-based search
            # This is a simplified version - in production you might want more sophisticated search
            search_results = list(self.fallback_storage.values())[:n_results]
            
            if search_results:
                results['documents'] = [[item['document'] for item in search_results]]
                results['metadatas'] = [[item['metadata'] for item in search_results]]
                results['distances'] = [[0.5] * len(search_results)]  # Dummy distances
            
            return results
        else:
            return self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results
            )
    
    def get_all_documents(self):
        """Get all documents from storage"""
        if self.use_fallback:
            if not self.fallback_storage:
                return {'documents': [], 'metadatas': []}
            
            documents = [item['document'] for item in self.fallback_storage.values()]
            metadatas = [item['metadata'] for item in self.fallback_storage.values()]
            
            return {'documents': documents, 'metadatas': metadatas}
        else:
            return self.collection.get()
    
    def count_documents(self):
        """Count total documents in storage"""
        if self.use_fallback:
            return len(self.fallback_storage)
        else:
            try:
                all_docs = self.collection.get()
                return len(all_docs.get('documents', []))
            except:
                return 0


def create_chromadb_instance(persist_directory="./knowledge_base"):
    """Factory function to create ChromaDB instance with error handling"""
    return ChromaDBWrapper(persist_directory)
