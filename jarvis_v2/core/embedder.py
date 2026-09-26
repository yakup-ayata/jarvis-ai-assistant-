#!/usr/bin/env python3
"""
JARVIS Embedder - Text to Vector Conversion
Uses sentence-transformers for offline semantic embeddings
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import torch

class Embedder:
    """
    Offline text embedder using sentence-transformers
    Converts text to semantic vectors for similarity search
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedder
        
        Args:
            model_name: Model to use
                - all-MiniLM-L6-v2: 384 dim, 80MB, fast (RECOMMENDED)
                - all-mpnet-base-v2: 768 dim, 420MB, accurate
        """
        self.model_name = model_name
        self.dimension = 384 if "MiniLM" in model_name else 768
        
        print(f"📦 Loading embedder model: {model_name}...")
        
        # Load model (will download on first run, then cached)
        self.model = SentenceTransformer(model_name)
        
        # Use GPU if available (Metal on Mac)
        if torch.backends.mps.is_available():
            self.device = "mps"
            self.model = self.model.to("mps")
            print(f"   ✓ Using Metal GPU acceleration")
        elif torch.cuda.is_available():
            self.device = "cuda"
            self.model = self.model.to("cuda")
            print(f"   ✓ Using CUDA GPU acceleration")
        else:
            self.device = "cpu"
            print(f"   ✓ Using CPU")
        
        print(f"   ✓ Embedder ready (dim={self.dimension}, device={self.device})")
    
    def encode(self, texts: Union[str, List[str]], 
               batch_size: int = 32,
               show_progress: bool = False) -> np.ndarray:
        """
        Encode text(s) to vector(s)
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for encoding
            show_progress: Show progress bar
        
        Returns:
            numpy array of shape (n, dimension)
        """
        # Handle single text
        if isinstance(texts, str):
            texts = [texts]
        
        # Encode
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode a single query (optimized)
        
        Args:
            query: Query text
        
        Returns:
            numpy array of shape (dimension,)
        """
        embedding = self.model.encode(query, convert_to_numpy=True)
        return embedding
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score (0-1)
        """
        emb1 = self.encode_query(text1)
        emb2 = self.encode_query(text2)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        return float(similarity)

def main():
    """Test embedder"""
    print("🧪 Testing Embedder...")
    print("=" * 60)
    
    # Create embedder
    embedder = Embedder()
    
    # Test single text
    print("\n1. Encoding single text...")
    text = "JARVIS is an AI assistant"
    embedding = embedder.encode_query(text)
    print(f"   Text: {text}")
    print(f"   Embedding shape: {embedding.shape}")
    print(f"   First 5 values: {embedding[:5]}")
    
    # Test batch encoding
    print("\n2. Encoding batch...")
    texts = [
        "Machine learning is fascinating",
        "Python is a programming language",
        "Vector databases enable semantic search"
    ]
    embeddings = embedder.encode(texts)
    print(f"   Encoded {len(texts)} texts")
    print(f"   Embeddings shape: {embeddings.shape}")
    
    # Test similarity
    print("\n3. Testing similarity...")
    text1 = "AI and machine learning"
    text2 = "Artificial intelligence and ML"
    text3 = "Cooking recipes"
    
    sim_12 = embedder.similarity(text1, text2)
    sim_13 = embedder.similarity(text1, text3)
    
    print(f"   '{text1}' vs '{text2}': {sim_12:.4f}")
    print(f"   '{text1}' vs '{text3}': {sim_13:.4f}")
    
    print("\n" + "=" * 60)
    print("✓ Embedder test complete")

if __name__ == "__main__":
    main()
