#!/usr/bin/env python3
"""
JARVIS Document Chunker - Smart text chunking
Splits documents into semantic chunks with overlap
"""

from typing import List, Dict
import re

class DocumentChunker:
    """
    Smart document chunker
    Splits text into overlapping chunks for better retrieval
    """
    
    def __init__(self, 
                 chunk_size: int = 512,
                 overlap: int = 50,
                 min_chunk_size: int = 100):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target chunk size in tokens (approx)
            overlap: Overlap between chunks in tokens
            min_chunk_size: Minimum chunk size to keep
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size
        
        print(f"✂️  Document Chunker initialized (size={chunk_size}, overlap={overlap})")
    
    def chunk(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Chunk text into overlapping segments
        
        Args:
            text: Text to chunk
            metadata: Base metadata to include in each chunk
        
        Returns:
            List of chunk dicts with text and metadata
        """
        if not text or not text.strip():
            return []
        
        # Split into sentences first (semantic boundaries)
        sentences = self._split_sentences(text)
        
        # Group sentences into chunks
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = self._estimate_tokens(sentence)
            
            # If adding this sentence exceeds chunk size
            if current_size + sentence_size > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append(chunk_text)
                
                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(current_chunk)
                current_chunk = overlap_sentences
                current_size = sum(self._estimate_tokens(s) for s in current_chunk)
            
            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if self._estimate_tokens(chunk_text) >= self.min_chunk_size:
                chunks.append(chunk_text)
        
        # Build chunk dicts with metadata
        result = []
        base_metadata = metadata or {}
        
        for i, chunk_text in enumerate(chunks):
            chunk_metadata = {
                **base_metadata,
                'chunk_id': i,
                'total_chunks': len(chunks),
                'chunk_size': self._estimate_tokens(chunk_text)
            }
            
            result.append({
                'text': chunk_text,
                'metadata': chunk_metadata
            })
        
        return result
    
    def chunk_document(self, document: Dict) -> List[Dict]:
        """
        Chunk a parsed document
        
        Args:
            document: Document dict from DocumentParser
        
        Returns:
            List of chunk dicts
        """
        text = document.get('text', '')
        metadata = document.get('metadata', {})
        
        # Add page information if available
        chunks = []
        pages = document.get('pages', [])
        
        if pages:
            # Chunk each page separately
            for page in pages:
                page_text = page.get('text', '')
                page_metadata = {
                    **metadata,
                    'page_num': page.get('page_num') or page.get('para_num') or page.get('section_num')
                }
                
                page_chunks = self.chunk(page_text, page_metadata)
                chunks.extend(page_chunks)
        else:
            # Chunk entire document
            chunks = self.chunk(text, metadata)
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (can be improved with NLTK)
        # Split on . ! ? followed by space and capital letter
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        
        # Clean up
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """Get sentences for overlap"""
        overlap_tokens = 0
        overlap_sentences = []
        
        # Take sentences from end until we reach overlap size
        for sentence in reversed(sentences):
            sentence_tokens = self._estimate_tokens(sentence)
            if overlap_tokens + sentence_tokens > self.overlap:
                break
            overlap_sentences.insert(0, sentence)
            overlap_tokens += sentence_tokens
        
        return overlap_sentences

def main():
    """Test document chunker"""
    print("🧪 Testing Document Chunker...")
    print("=" * 60)
    
    # Create chunker
    chunker = DocumentChunker(chunk_size=100, overlap=20)
    
    # Test text
    test_text = """
    JARVIS is an advanced AI assistant. It can understand natural language.
    The system uses machine learning for intelligent responses. It processes
    user queries in real-time. JARVIS can control system functions. It has
    memory and reflection capabilities. The assistant learns from interactions.
    It provides helpful and accurate information. JARVIS is designed for
    productivity and efficiency. The system runs completely offline.
    """
    
    print("\n1. Chunking text...")
    chunks = chunker.chunk(test_text.strip(), {'source': 'test.txt'})
    
    print(f"   Created {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\n   Chunk {i + 1}:")
        print(f"   Size: {chunk['metadata']['chunk_size']} tokens")
        print(f"   Text: {chunk['text'][:80]}...")
    
    # Test document chunking
    print("\n2. Chunking document...")
    test_doc = {
        'text': test_text.strip(),
        'metadata': {'source': 'test.txt', 'format': 'txt'},
        'pages': [
            {'para_num': 1, 'text': test_text.strip()}
        ]
    }
    
    doc_chunks = chunker.chunk_document(test_doc)
    print(f"   Created {len(doc_chunks)} chunks from document")
    
    print("\n" + "=" * 60)
    print("✓ Document Chunker test complete")

if __name__ == "__main__":
    main()
