#!/usr/bin/env python3
"""
JARVIS RAG Engine - Retrieval-Augmented Generation
Combines document retrieval with LLM for context-aware responses
"""

import asyncio
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json
import time

from vector_store import VectorStore
from embedder import Embedder
from document_parser import DocumentParser
from document_chunker import DocumentChunker

# Singleton embedder instance (shared across all RAG engines)
_embedder_instance = None
_embedder_lock = asyncio.Lock()

async def get_embedder(model_name: str = "all-MiniLM-L6-v2") -> Embedder:
    """Get singleton embedder instance"""
    global _embedder_instance
    
    if _embedder_instance is None:
        async with _embedder_lock:
            if _embedder_instance is None:
                print("🔧 Initializing shared embedder...")
                _embedder_instance = Embedder(model_name=model_name)
                print("   ✓ Embedder ready")
    
    return _embedder_instance

class RAGEngine:
    """
    RAG Engine for document-based question answering
    Query → Search → Context → LLM → Answer
    Uses singleton embedder for efficiency
    """
    
    def __init__(self, 
                 storage_path: str = "jarvis_v2/data/vector_store",
                 model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize RAG engine
        
        Args:
            storage_path: Path to store vector database
            model_name: Embedding model name
        """
        print("🧠 Initializing RAG Engine...")
        
        # Use singleton embedder (will be initialized on first use)
        self.embedder = None
        self.model_name = model_name
        self._embedder_initialized = False
        
        # Initialize other components
        self.vector_store = None
        self.storage_path = storage_path
        self.parser = DocumentParser()
        self.chunker = DocumentChunker(chunk_size=512, overlap=50)
        
        # LLM reference (will be set externally)
        self.llm = None
        
        print("✓ RAG Engine ready (embedder will load on first use)")
    
    async def _ensure_embedder(self):
        """Ensure embedder is initialized (lazy loading)"""
        if not self._embedder_initialized:
            self.embedder = await get_embedder(self.model_name)
            
            # Initialize vector store now that we have embedder dimension
            if self.vector_store is None:
                self.vector_store = VectorStore(
                    dimension=self.embedder.dimension,
                    storage_path=self.storage_path
                )
            
            self._embedder_initialized = True
    
    def set_llm(self, llm):
        """Set LLM instance for generation"""
        self.llm = llm
        print("   ✓ LLM connected to RAG Engine")
    
    async def add_document(self, file_path: str) -> Dict:
        """
        Add document to RAG system
        
        Args:
            file_path: Path to document file
        
        Returns:
            Dict with processing stats
        """
        await self._ensure_embedder()  # Ensure embedder is loaded
        
        start_time = time.time()
        
        print(f"\n📄 Processing document: {file_path}")
        
        # 1. Parse document
        print("   1/4 Parsing document...")
        document = self.parser.parse(file_path)
        print(f"       ✓ Extracted {len(document['text'])} characters")
        
        # 2. Chunk document
        print("   2/4 Chunking document...")
        chunks = self.chunker.chunk_document(document)
        print(f"       ✓ Created {len(chunks)} chunks")
        
        # 3. Embed chunks
        print("   3/4 Embedding chunks...")
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedder.encode(chunk_texts, show_progress=False)
        print(f"       ✓ Generated {len(embeddings)} embeddings")
        
        # 4. Store in vector database
        print("   4/4 Storing in vector database...")
        chunk_metadata = [chunk['metadata'] for chunk in chunks]
        self.vector_store.add(embeddings, chunk_texts, chunk_metadata)
        self.vector_store.save()
        print(f"       ✓ Stored in database")
        
        elapsed = time.time() - start_time
        
        stats = {
            'file': Path(file_path).name,
            'format': document['metadata']['format'],
            'chunks': len(chunks),
            'characters': len(document['text']),
            'processing_time': f"{elapsed:.2f}s"
        }
        
        print(f"\n✓ Document processed in {elapsed:.2f}s")
        
        return stats
    
    async def query(self, 
                   question: str, 
                   k: int = 3,
                   threshold: float = 1.5) -> Dict:
        """
        Query RAG system
        
        Args:
            question: User question
            k: Number of documents to retrieve
            threshold: Distance threshold for relevance
        
        Returns:
            Dict with answer and sources
        """
        await self._ensure_embedder()  # Ensure embedder is loaded
        
        start_time = time.time()
        
        print(f"\n🔍 RAG Query: {question}")
        
        # 1. Embed query
        print("   1/3 Embedding query...")
        query_embedding = self.embedder.encode_query(question)
        
        # 2. Search vector database
        print("   2/3 Searching documents...")
        results = self.vector_store.search_with_threshold(
            query_embedding, 
            k=k, 
            threshold=threshold
        )
        
        if not results:
            print("   ⚠️  No relevant documents found")
            return {
                'answer': "I don't have any relevant documents to answer that question, sir.",
                'sources': [],
                'context_used': False
            }
        
        print(f"       ✓ Found {len(results)} relevant chunks")
        
        # 3. Build context
        context_parts = []
        sources = []
        
        for i, (doc_text, metadata, distance) in enumerate(results):
            context_parts.append(f"[Document {i+1}]\n{doc_text}")
            sources.append({
                'source': metadata.get('source', 'unknown'),
                'chunk': metadata.get('chunk_id', 0),
                'relevance': float(1.0 / (1.0 + distance))  # Convert distance to relevance score
            })
        
        context = "\n\n".join(context_parts)
        
        # 4. Generate answer with LLM
        print("   3/3 Generating answer...")
        
        if self.llm:
            # Build prompt with context
            prompt = self._build_prompt(question, context)
            
            # Generate answer
            answer = await self._generate_answer(prompt)
        else:
            # Fallback if no LLM
            answer = f"Based on the documents: {context[:200]}..."
        
        elapsed = time.time() - start_time
        
        print(f"✓ Answer generated in {elapsed:.2f}s")
        
        return {
            'answer': answer,
            'sources': sources,
            'context_used': True,
            'processing_time': f"{elapsed:.2f}s"
        }
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Build prompt for LLM with context"""
        prompt = f"""You are JARVIS, an AI assistant. Answer the question based on the provided context.

Context from documents:
{context}

Question: {question}

Instructions:
- Answer based on the context provided
- If the context doesn't contain the answer, say so
- Be concise and accurate
- Address the user as "sir" (JARVIS style)

Answer:"""
        
        return prompt
    
    async def _generate_answer(self, prompt: str) -> str:
        """Generate answer using LLM"""
        try:
            if hasattr(self.llm, 'generate'):
                # Sync LLM
                answer = self.llm.generate(prompt)
            elif hasattr(self.llm, 'agenerate'):
                # Async LLM
                answer = await self.llm.agenerate(prompt)
            else:
                # Fallback
                answer = "I apologize, sir. The LLM interface is not properly configured."
            
            return answer
            
        except Exception as e:
            print(f"   ✗ Error generating answer: {e}")
            return "I apologize, sir. I encountered an error generating the answer."
    
    def delete_document(self, source: str) -> int:
        """
        Delete all chunks from a document
        
        Args:
            source: Document source name
        
        Returns:
            Number of chunks deleted
        """
        count = self.vector_store.delete_by_source(source)
        if count > 0:
            self.vector_store.save()
        return count
    
    def list_documents(self) -> List[Dict]:
        """
        List all documents in the system
        
        Returns:
            List of document info dicts
        """
        stats = self.vector_store.get_stats()
        sources = stats.get('sources', {})
        
        documents = []
        for source, chunk_count in sources.items():
            documents.append({
                'source': source,
                'chunks': chunk_count
            })
        
        return documents
    
    def get_stats(self) -> Dict:
        """Get RAG system statistics"""
        return self.vector_store.get_stats()

async def main():
    """Test RAG engine"""
    print("🧪 Testing RAG Engine...")
    print("=" * 60)
    
    # Create RAG engine
    rag = RAGEngine(storage_path="test_vector_store")
    
    # Create test document
    print("\n1. Creating test document...")
    test_file = Path("test_rag_doc.txt")
    test_content = """JARVIS AI Assistant

JARVIS is an advanced artificial intelligence assistant designed to help users
with various tasks. It uses machine learning and natural language processing
to understand and respond to user queries.

Key Features:
- Natural language understanding
- Task automation
- System control
- Memory and learning capabilities
- Completely offline operation

Technical Details:
JARVIS uses Ollama for local LLM processing, ensuring complete privacy and
offline functionality. The system includes RAG (Retrieval-Augmented Generation)
for document-based question answering.

Performance:
The system runs efficiently on Apple Silicon (M1/M2/M3) with 16GB RAM.
Response times are typically under 2 seconds for most queries."""
    
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print(f"   ✓ Created {test_file}")
    
    # Add document
    print("\n2. Adding document to RAG...")
    stats = await rag.add_document(str(test_file))
    print(f"   Stats: {stats}")
    
    # Query RAG
    print("\n3. Querying RAG...")
    result = await rag.query("What are the key features of JARVIS?")
    print(f"   Answer: {result['answer'][:100]}...")
    print(f"   Sources: {len(result['sources'])}")
    
    # List documents
    print("\n4. Listing documents...")
    docs = rag.list_documents()
    for doc in docs:
        print(f"   - {doc['source']}: {doc['chunks']} chunks")
    
    # Clean up
    test_file.unlink()
    import shutil
    shutil.rmtree("test_vector_store", ignore_errors=True)
    print(f"\n   ✓ Cleaned up test files")
    
    print("\n" + "=" * 60)
    print("✓ RAG Engine test complete")

if __name__ == "__main__":
    asyncio.run(main())
