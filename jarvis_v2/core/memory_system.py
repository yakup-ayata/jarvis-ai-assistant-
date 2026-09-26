#!/usr/bin/env python3
"""
JARVIS Memory System - Phase 4
Short-term and Long-term memory with vector search
"""

import json
import time
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np

@dataclass
class MemoryEntry:
    """Single memory entry"""
    id: str
    timestamp: float
    type: str  # "query", "action", "event", "reflection"
    content: str
    metadata: Dict
    embedding: Optional[List[float]] = None
    importance: float = 0.5  # 0-1 scale
    
    def to_dict(self) -> Dict:
        """Convert memory entry to dictionary"""
        data = asdict(self)
        # Convert numpy array to list if needed
        if self.embedding is not None and isinstance(self.embedding, np.ndarray):
            data['embedding'] = self.embedding.tolist()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict):
        # Convert list back to numpy array if needed
        if data.get('embedding') is not None:
            data['embedding'] = np.array(data['embedding'])
        return cls(**data)

class ShortTermMemory:
    """
    Short-term memory - Recent interactions
    Fast access, limited capacity
    """
    
    def __init__(self, max_entries: int = 100):
        self.max_entries = max_entries
        self.entries: List[MemoryEntry] = []
        self.entry_index: Dict[str, MemoryEntry] = {}
    
    def add(self, entry: MemoryEntry) -> None:
        """Add entry to short-term memory"""
        self.entries.append(entry)
        self.entry_index[entry.id] = entry
        
        # Trim if exceeds capacity
        if len(self.entries) > self.max_entries:
            removed = self.entries.pop(0)
            del self.entry_index[removed.id]
    
    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get entry by ID"""
        return self.entry_index.get(entry_id)
    
    def get_recent(self, n: int = 10) -> List[MemoryEntry]:
        """Get N most recent entries"""
        return self.entries[-n:]
    
    def get_by_type(self, entry_type: str, n: int = 10) -> List[MemoryEntry]:
        """Get recent entries of specific type"""
        filtered = [e for e in self.entries if e.type == entry_type]
        return filtered[-n:]
    
    def search(self, query: str, n: int = 5) -> List[MemoryEntry]:
        """Simple keyword search"""
        query_lower = query.lower()
        results = []
        
        for entry in reversed(self.entries):
            if query_lower in entry.content.lower():
                results.append(entry)
                if len(results) >= n:
                    break
        
        return results
    
    def clear_old(self, hours: int = 24) -> None:
        """Clear entries older than N hours"""
        cutoff = time.time() - (hours * 3600)
        self.entries = [e for e in self.entries if e.timestamp > cutoff]
        
        # Rebuild index
        self.entry_index = {e.id: e for e in self.entries}
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        if not self.entries:
            return {"total": 0}
        
        types = {}
        for entry in self.entries:
            types[entry.type] = types.get(entry.type, 0) + 1
        
        return {
            "total": len(self.entries),
            "capacity": self.max_entries,
            "usage_percent": (len(self.entries) / self.max_entries) * 100,
            "types": types,
            "oldest": datetime.fromtimestamp(self.entries[0].timestamp).isoformat(),
            "newest": datetime.fromtimestamp(self.entries[-1].timestamp).isoformat()
        }

class LongTermMemory:
    """
    Long-term memory - Persistent storage with vector search
    Uses FAISS for semantic search
    """
    
    def __init__(self, storage_dir: str = "data/memory"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.entries_file = self.storage_dir / "long_term_memory.json"
        self.vectors_file = self.storage_dir / "vectors.pkl"
        
        self.entries: List[MemoryEntry] = []
        self.entry_index: Dict[str, MemoryEntry] = {}
        
        # Vector search (FAISS will be initialized when needed)
        self.vector_index = None
        self.embedding_dim = 384  # Default for sentence-transformers
        
        # Load existing memories
        self._load()
    
    def _load(self) -> None:
        """Load memories from disk"""
        if self.entries_file.exists():
            try:
                with open(self.entries_file, 'r') as f:
                    data = json.load(f)
                    self.entries = [MemoryEntry.from_dict(e) for e in data]
                    self.entry_index = {e.id: e for e in self.entries}
            except Exception as e:
                print(f"Error loading long-term memory: {e}")
        
        # Load vector index
        if self.vectors_file.exists():
            try:
                with open(self.vectors_file, 'rb') as f:
                    self.vector_index = pickle.load(f)
            except Exception as e:
                print(f"Error loading vector index: {e}")
    
    def _save(self) -> None:
        """Save memories to disk with atomic write"""
        try:
            # Write to temporary file first (atomic write pattern)
            temp_file = self.entries_file.with_suffix('.tmp')
            
            with open(temp_file, 'w') as f:
                data = [e.to_dict() for e in self.entries]
                json.dump(data, f, indent=2)
            
            # Atomic rename (replaces old file)
            temp_file.replace(self.entries_file)
            
            # Save vector index
            if self.vector_index is not None:
                temp_vectors = self.vectors_file.with_suffix('.tmp')
                with open(temp_vectors, 'wb') as f:
                    pickle.dump(self.vector_index, f)
                temp_vectors.replace(self.vectors_file)
                
        except Exception as e:
            print(f"Error saving long-term memory: {e}")
            # Clean up temp files if they exist
            temp_file = self.entries_file.with_suffix('.tmp')
            if temp_file.exists():
                temp_file.unlink()
            temp_vectors = self.vectors_file.with_suffix('.tmp')
            if temp_vectors.exists():
                temp_vectors.unlink()
    
    def add(self, entry: MemoryEntry) -> None:
        """Add entry to long-term memory"""
        self.entries.append(entry)
        self.entry_index[entry.id] = entry
        
        # Save periodically (every 10 entries)
        if len(self.entries) % 10 == 0:
            self._save()
    
    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get entry by ID"""
        return self.entry_index.get(entry_id)
    
    def search_keyword(self, query: str, n: int = 10) -> List[MemoryEntry]:
        """Keyword-based search"""
        query_lower = query.lower()
        results = []
        
        for entry in reversed(self.entries):
            if query_lower in entry.content.lower():
                results.append(entry)
                if len(results) >= n:
                    break
        
        return results
    
    def search_semantic(self, query_embedding: np.ndarray, n: int = 10) -> List[Tuple[MemoryEntry, float]]:
        """
        Semantic search using vector similarity
        Returns list of (entry, similarity_score) tuples
        """
        if not self.entries:
            return []
        
        # Simple cosine similarity (FAISS would be better for large datasets)
        results = []
        
        for entry in self.entries:
            if entry.embedding is not None:
                # Cosine similarity
                similarity = np.dot(query_embedding, entry.embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(entry.embedding)
                )
                results.append((entry, float(similarity)))
        
        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:n]
    
    def get_by_importance(self, threshold: float = 0.7, n: int = 10) -> List[MemoryEntry]:
        """Get important memories"""
        important = [e for e in self.entries if e.importance >= threshold]
        important.sort(key=lambda x: x.importance, reverse=True)
        return important[:n]
    
    def consolidate(self, short_term: ShortTermMemory, importance_threshold: float = 0.6) -> None:
        """
        Consolidate important short-term memories to long-term
        """
        for entry in short_term.entries:
            if entry.importance >= importance_threshold:
                # Check if not already in long-term
                if entry.id not in self.entry_index:
                    self.add(entry)
        
        self._save()
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        if not self.entries:
            return {"total": 0}
        
        types = {}
        importance_sum = 0
        
        for entry in self.entries:
            types[entry.type] = types.get(entry.type, 0) + 1
            importance_sum += entry.importance
        
        return {
            "total": len(self.entries),
            "types": types,
            "avg_importance": importance_sum / len(self.entries),
            "has_embeddings": sum(1 for e in self.entries if e.embedding is not None),
            "oldest": datetime.fromtimestamp(self.entries[0].timestamp).isoformat() if self.entries else None,
            "newest": datetime.fromtimestamp(self.entries[-1].timestamp).isoformat() if self.entries else None
        }

class MemorySystem:
    """
    Unified memory system combining short-term and long-term memory
    """
    
    def __init__(self):
        self.short_term = ShortTermMemory(max_entries=100)
        self.long_term = LongTermMemory()
        
        # Memory consolidation settings
        self.consolidation_interval = 3600  # 1 hour
        self.last_consolidation = time.time()
    
    def remember(self, content: str, entry_type: str = "query", 
                 metadata: Dict = None, importance: float = 0.5) -> MemoryEntry:
        """
        Store a new memory
        """
        entry = MemoryEntry(
            id=f"{entry_type}_{int(time.time() * 1000)}",
            timestamp=time.time(),
            type=entry_type,
            content=content,
            metadata=metadata or {},
            importance=importance
        )
        
        # Add to short-term memory
        self.short_term.add(entry)
        
        # If important, also add to long-term
        if importance >= 0.7:
            self.long_term.add(entry)
        
        # Periodic consolidation
        if time.time() - self.last_consolidation > self.consolidation_interval:
            self.consolidate()
        
        return entry
    
    def recall(self, query: str, n: int = 5) -> List[MemoryEntry]:
        """
        Recall memories related to query
        Searches both short-term and long-term
        """
        # Search short-term
        short_results = self.short_term.search(query, n)
        
        # Search long-term
        long_results = self.long_term.search_keyword(query, n)
        
        # Combine and deduplicate
        all_results = short_results + long_results
        seen_ids = set()
        unique_results = []
        
        for entry in all_results:
            if entry.id not in seen_ids:
                seen_ids.add(entry.id)
                unique_results.append(entry)
        
        return unique_results[:n]
    
    def consolidate(self) -> None:
        """
        Move important short-term memories to long-term
        """
        self.long_term.consolidate(self.short_term, importance_threshold=0.6)
        self.last_consolidation = time.time()
        
        # Clear old short-term memories
        self.short_term.clear_old(hours=24)
    
    def get_context(self, n: int = 5) -> str:
        """
        Get recent context as string (for LLM prompts)
        """
        recent = self.short_term.get_recent(n)
        
        context_lines = []
        for entry in recent:
            timestamp = datetime.fromtimestamp(entry.timestamp).strftime("%H:%M:%S")
            context_lines.append(f"[{timestamp}] {entry.type}: {entry.content}")
        
        return "\n".join(context_lines)
    
    def get_stats(self) -> Dict:
        """Get overall memory statistics"""
        return {
            "short_term": self.short_term.get_stats(),
            "long_term": self.long_term.get_stats(),
            "last_consolidation": datetime.fromtimestamp(self.last_consolidation).isoformat()
        }

def main() -> None:
    """Test memory system"""
    memory = MemorySystem()
    
    print("🧠 JARVIS Memory System - Test")
    print("=" * 60)
    
    # Add some memories
    print("\n1. Adding memories...")
    memory.remember("User asked to open Instagram", "query", importance=0.5)
    memory.remember("Opened Instagram successfully", "action", importance=0.6)
    memory.remember("User asked about Python", "query", importance=0.7)
    memory.remember("Provided Python tutorial", "action", importance=0.8)
    memory.remember("System CPU usage high", "event", importance=0.9)
    
    # Recall memories
    print("\n2. Recalling memories about 'Instagram'...")
    results = memory.recall("Instagram", n=3)
    for entry in results:
        print(f"   - [{entry.type}] {entry.content} (importance: {entry.importance})")
    
    print("\n3. Recalling memories about 'Python'...")
    results = memory.recall("Python", n=3)
    for entry in results:
        print(f"   - [{entry.type}] {entry.content} (importance: {entry.importance})")
    
    # Get context
    print("\n4. Recent context:")
    context = memory.get_context(n=5)
    print(context)
    
    # Statistics
    print("\n5. Memory statistics:")
    stats = memory.get_stats()
    print(f"   Short-term: {stats['short_term']['total']} entries")
    print(f"   Long-term: {stats['long_term']['total']} entries")
    
    # Consolidate
    print("\n6. Consolidating memories...")
    memory.consolidate()
    stats = memory.get_stats()
    print(f"   Long-term after consolidation: {stats['long_term']['total']} entries")
    
    print("\n" + "=" * 60)
    print("✓ Memory system test complete")

if __name__ == "__main__":
    main()
