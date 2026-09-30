"""
Step 4 of Ingestion & Step 3 of Query Phase: Vector Database Store & Search Engine
Stores vector embeddings and performs Cosine Similarity search to find top-K matching chunks.
"""
import math
import json
import os

class LocalVectorDB:
    def __init__(self, db_path="./vector_store.json"):
        self.db_path = db_path
        self.chunks = []
        self.load()

    def add_chunks(self, chunks_with_embeddings):
        """Stores chunk records (text, metadata, and embedding vectors)."""
        self.chunks.extend(chunks_with_embeddings)
        self.save()
        print(f"💾 Stored {len(chunks_with_embeddings)} vector records in Vector DB ({self.db_path}).")

    def search(self, query_vector, top_k=3):
        """
        Performs Cosine Similarity search between query_vector and all stored chunk vectors.
        Returns top-K matching chunks with similarity scores (0.0 to 1.0).
        """
        if not self.chunks:
            print("⚠️ Vector DB is empty.")
            return []

        scored_chunks = []
        for chunk in self.chunks:
            chunk_vec = chunk["embedding"]
            score = self.cosine_similarity(query_vector, chunk_vec)
            scored_chunks.append({
                "chunk": chunk,
                "score": score
            })

        # Sort by similarity score in descending order
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

    @staticmethod
    def cosine_similarity(vec1, vec2):
        """Calculates cosine similarity between two float vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = math.sqrt(sum(a * a for a in vec1))
        norm_b = math.sqrt(sum(b * b for b in vec2))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def save(self):
        """Persists vector database to disk."""
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self.chunks, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving vector DB: {e}")

    def load(self):
        """Loads vector database from disk."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading vector DB: {e}")
                self.chunks = []
