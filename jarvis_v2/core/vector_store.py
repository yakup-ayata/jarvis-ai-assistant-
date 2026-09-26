#!/usr/bin/env python3
"""
JARVIS Vector Store - FAISS-based semantic search
Offline vector database for document retrieval
"""

import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import json

class VectorStore:
    """
    FAISS-based vector store for semantic search
    Stores document chunks and their embeddings
    """
    
    def __init__(self, dimension: int = 384, storage_path: str = "data/vector_store"):
        """
        Initialize vector store
        
        Args:
            dimension: Embedding dimension (384 for MiniLM, 768 for MPNet)
            storage_path: Path to store index and metadata
        """
        self.dimension = dimension
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # FAISS index (L2 distance)
        self.index = faiss.IndexFlatL2(dimension)
        
        # Document metadata
        self.documents = []  # List of document chunks
        self.metadata = []   # List of metadata dicts
        
        # Load existing index if available
        self._load()
        
        print(f"📊 Vector Store initialized (dim={dimension}, docs={len(self.documents)})")
    
    def add(self, vectors: np.ndarray, documents: List[str], metadata: List[Dict]):
        """
        Add vectors and documents to the store
        
        Args:
            vectors: numpy array of shape (n, dimension)
            documents: List of document text chunks
            metadata: List of metadata dicts (source, page, etc.)
        """
        if len(vectors) != len(documents) or len(vectors) != len(metadata):
            raise ValueError("Vectors, documents, and metadata must have same length")
        
        # Add to FAISS index
        vectors_float32 = vectors.astype('float32')
        self.index.add(vectors_float32)
        
        # Store documents and metadata
        self.documents.extend(documents)
        self.metadata.extend(metadata)
        
        print(f"   ✓ Added {len(vectors)} vectors to store (total: {len(self.documents)})")
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Tuple[str, Dict, float]]:
        """
        Search for similar documents
        
        Args:
            query_vector: Query embedding vector
            k: Number of results to return
        
        Returns:
            List of (document, metadata, distance) tuples
        """
        if len(self.documents) == 0:
            return []
        
        # Ensure k doesn't exceed number of documents
        k = min(k, len(self.documents))
        
        # Search FAISS index
        query_float32 = query_vector.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_float32, k)
        
        # Build results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):  # Safety check
                results.append((
                    self.documents[idx],
                    self.metadata[idx],
                    float(distances[0][i])
                ))
        
        return results
    
    def search_with_threshold(self, query_vector: np.ndarray, 
                             k: int = 5, 
                             threshold: float = 1.0) -> List[Tuple[str, Dict, float]]:
        """
        Search with distance threshold
        
        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            threshold: Maximum distance threshold
        
        Returns:
            List of (document, metadata, distance) tuples within threshold
        """
        results = self.search(query_vector, k)
        return [(doc, meta, dist) for doc, meta, dist in results if dist <= threshold]
    
    def get_by_source(self, source: str) -> List[Tuple[str, Dict]]:
        """
        Get all documents from a specific source
        
        Args:
            source: Source identifier (filename, URL, etc.)
        
        Returns:
            List of (document, metadata) tuples
        """
        results = []
        for doc, meta in zip(self.documents, self.metadata):
            if meta.get('source') == source:
                results.append((doc, meta))
        return results
    
    def delete_by_source(self, source: str) -> int:
        """
        Delete all documents from a specific source
        
        Args:
            source: Source identifier
        
        Returns:
            Number of documents deleted
        """
        # Find indices to keep
        keep_indices = [
            i for i, meta in enumerate(self.metadata)
            if meta.get('source') != source
        ]
        
        deleted_count = len(self.documents) - len(keep_indices)
        
        if deleted_count > 0:
            # Rebuild index with remaining documents
            self.documents = [self.documents[i] for i in keep_indices]
            self.metadata = [self.metadata[i] for i in keep_indices]
            
            # Rebuild FAISS index
            self.index = faiss.IndexFlatL2(self.dimension)
            
            print(f"   ✓ Deleted {deleted_count} documents from '{source}'")
        
        return deleted_count
    
    def clear(self):
        """Clear all documents and reset index"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.metadata = []
        print("   ✓ Vector store cleared")
    
    def save(self):
        """Save index and metadata to disk"""
        try:
            # Save FAISS index
            index_path = self.storage_path / "faiss.index"
            faiss.write_index(self.index, str(index_path))
            
            # Save documents and metadata
            data_path = self.storage_path / "documents.pkl"
            with open(data_path, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'metadata': self.metadata,
                    'dimension': self.dimension
                }, f)
            
            print(f"   ✓ Vector store saved ({len(self.documents)} documents)")
            
        except Exception as e:
            print(f"   ✗ Error saving vector store: {e}")
    
    def _load(self):
        """Load index and metadata from disk"""
        try:
            index_path = self.storage_path / "faiss.index"
            data_path = self.storage_path / "documents.pkl"
            
            if index_path.exists() and data_path.exists():
                # Load FAISS index
                self.index = faiss.read_index(str(index_path))
                
                # Load documents and metadata
                with open(data_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data['documents']
                    self.metadata = data['metadata']
                    
                    # Verify dimension matches
                    if data['dimension'] != self.dimension:
                        print(f"   ⚠️  Dimension mismatch: {data['dimension']} vs {self.dimension}")
                        print("   ⚠️  Clearing store...")
                        self.clear()
                
                print(f"   ✓ Loaded {len(self.documents)} documents from disk")
                
        except Exception as e:
            print(f"   ℹ️  No existing vector store found (will create new)")
    
    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        sources = {}
        for meta in self.metadata:
            source = meta.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        return {
            'total_documents': len(set(meta.get('source', '') for meta in self.metadata)),
            'total_chunks': len(self.documents),
            'dimension': self.dimension,
            'sources': sources,
            'index_size': self.index.ntotal
        }

def main():
    """Test vector store"""
    print("🧪 Testing Vector Store...")
    print("=" * 60)
    
    # Create store
    store = VectorStore(dimension=384)
    
    # Test data
    print("\n1. Adding test vectors...")
    test_vectors = np.random.rand(5, 384).astype('float32')
    test_docs = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is a subset of artificial intelligence",
        "Python is a popular programming language",
        "JARVIS is an AI assistant",
        "Vector databases enable semantic search"
    ]
    test_metadata = [
        {'source': 'test.txt', 'chunk': 0},
        {'source': 'test.txt', 'chunk': 1},
        {'source': 'test.txt', 'chunk': 2},
        {'source': 'test2.txt', 'chunk': 0},
        {'source': 'test2.txt', 'chunk': 1}
    ]
    
    store.add(test_vectors, test_docs, test_metadata)
    
    # Test search
    print("\n2. Testing search...")
    query_vector = np.random.rand(384).astype('float32')
    results = store.search(query_vector, k=3)
    
    print(f"   Found {len(results)} results:")
    for doc, meta, dist in results:
        print(f"   - {doc[:50]}... (distance: {dist:.4f})")
    
    # Test get by source
    print("\n3. Testing get by source...")
    source_docs = store.get_by_source('test.txt')
    print(f"   Found {len(source_docs)} documents from 'test.txt'")
    
    # Test stats
    print("\n4. Statistics:")
    stats = store.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test save/load
    print("\n5. Testing save...")
    store.save()
    
    print("\n" + "=" * 60)
    print("✓ Vector Store test complete")

if __name__ == "__main__":
    main()
