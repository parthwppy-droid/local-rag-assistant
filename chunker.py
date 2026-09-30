"""
Step 2 of Ingestion Phase: Text Chunker
Splits document text into manageable chunks (~300-500 words each) with overlap to preserve semantic context.
"""

class TextChunker:
    def __init__(self, chunk_size_words=300, overlap_words=50):
        self.chunk_size = chunk_size_words
        self.overlap = overlap_words

    def chunk_document(self, document):
        """
        Splits a single document object into a list of chunk objects.
        Each chunk contains metadata (source filename, chunk index, text).
        """
        content = document["content"]
        filename = document["filename"]
        words = content.split()
        
        chunks = []
        if not words:
            return chunks

        step = self.chunk_size - self.overlap
        if step <= 0:
            step = self.chunk_size

        chunk_idx = 0
        for i in range(0, len(words), step):
            chunk_words = words[i : i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "chunk_id": f"{filename}_chunk_{chunk_idx}",
                "source": filename,
                "chunk_index": chunk_idx,
                "text": chunk_text,
                "word_count": len(chunk_words)
            })
            chunk_idx += 1
            
            if i + self.chunk_size >= len(words):
                break

        return chunks

    def chunk_all(self, documents):
        """Chunks a list of documents."""
        all_chunks = []
        for doc in documents:
            doc_chunks = self.chunk_document(doc)
            all_chunks.extend(doc_chunks)
        print(f"✂️ Split {len(documents)} document(s) into {len(all_chunks)} chunk(s) (~{self.chunk_size} words each).")
        return all_chunks
