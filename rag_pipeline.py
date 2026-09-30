"""
Local RAG Pipeline Orchestrator (With Live Web Search & Local Document RAG)
Binds Ingestion, Local Document Retrieval, Live Web Search, and LLM Generation.
"""
import os
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from document_loader import DocumentLoader
from chunker import TextChunker
from embedder import VectorEmbedder
from vector_db import LocalVectorDB
from prompt_builder import PromptBuilder
from local_llm import LocalLLM
from web_search import LiveWebSearch

class LocalRAGPipeline:
    def __init__(self, docs_dir="./sample_docs", db_path="./vector_store.json"):
        self.docs_dir = docs_dir
        self.loader = DocumentLoader(docs_dir)
        self.chunker = TextChunker(chunk_size_words=300, overlap_words=50)
        vocab_path = db_path.replace(".json", ".vocab.json")
        self.embedder = VectorEmbedder(vocab_path=vocab_path)
        self.vector_db = LocalVectorDB(db_path)
        self.llm = LocalLLM()

        # Honest startup diagnostics — makes it obvious which mode is active
        # instead of discovering it mid-demo.
        print("\n" + "-"*60)
        print("[STARTUP CHECK]")
        if self.embedder.using_semantic_model:
            print("  Embeddings : ✅ real semantic model (sentence-transformers)")
        else:
            print("  Embeddings : ⚠️  TF-IDF fallback (keyword match only, not semantic)")
        model_name = self.llm.get_available_model()
        if model_name:
            print(f"  Local LLM  : ✅ Ollama reachable, using model '{model_name}'")
        else:
            print("  Local LLM  : ⚠️  Ollama not reachable — answers will use the fallback")
            print("               knowledge engine, not real generation.")
        print("-"*60 + "\n")

    def run_ingestion(self):
        """Executes Phase 1: Ingestion Pipeline."""
        print("\n" + "="*60)
        print("[PHASE 1] DOCUMENT INGESTION PIPELINE")
        print("="*60)

        # 1. Load documents
        documents = self.loader.load_documents()
        if not documents:
            print("[WARN] No documents found to ingest.")
            return 0

        # 2. Split into chunks (~300-500 words each)
        chunks = self.chunker.chunk_all(documents)

        # 3. Embed each chunk (Text turned into vector)
        chunks_with_vectors = self.embedder.embed_chunks(chunks)

        # 4. Store in vector DB
        self.vector_db.add_chunks(chunks_with_vectors)
        print("[OK] Phase 1 Ingestion Complete!\n")
        return len(chunks_with_vectors)

    def query(self, question, top_k=3):
        """Executes Phase 2: Universal Question, Web Search & Retrieval Pipeline."""
        print("\n" + "="*60)
        print("[PHASE 2] UNIVERSAL RETRIEVAL & GENERATION")
        print("="*60)
        print(f"User Question: \"{question}\"")

        # 1. Embed user question
        print("[STEP 1] Embedding user question...")
        q_vector = self.embedder.embed_text(question)

        # 2. Search Local Vector DB
        print(f"[STEP 2] Searching Vector DB for Top-{top_k} matching chunks...")
        matched_results = self.vector_db.search(q_vector, top_k=top_k)

        # NOTE: 0.70 was calibrated for real semantic embeddings, where a
        # genuinely relevant match usually scores high. TF-IDF cosine scores
        # behave very differently — a short question vs. a long chunk gets
        # "diluted" by all the chunk's other words, so even a correct match
        # often scores much lower. Using one fixed threshold for both modes
        # was quietly causing real matches to fall through to web search.
        local_match_threshold = 0.70 if self.embedder.using_semantic_model else 0.15

        top_score = matched_results[0]["score"] if matched_results else 0.0
        print(f"[DEBUG] Top match score: {top_score:.4f}  (threshold: {local_match_threshold}, "
              f"mode: {'semantic' if self.embedder.using_semantic_model else 'TF-IDF fallback'})")

        is_local_match = matched_results and top_score >= local_match_threshold

        # 3. If not in local docs, trigger Live Web Search!
        web_result = None
        if not is_local_match:
            print("[STEP 2.5] Question not in local docs. Triggering Live Web Search...")
            web_result = LiveWebSearch.live_search(question)
            if web_result:
                print(f"[OK] Fetched live information from [{web_result['source']}].")

        # 4. Build augmented prompt
        print("[STEP 3] Building Augmented Prompt...")
        augmented_prompt = PromptBuilder.build_augmented_prompt(
            question, matched_results, similarity_threshold=local_match_threshold
        )

        # 5. Universal LLM Generation
        print("[STEP 4] Universal AI Generating Answer...")
        answer = self.llm.generate_answer(
            augmented_prompt, 
            raw_question=question, 
            matched_chunks=matched_results if is_local_match else [],
            web_result=web_result
        )

        return {
            "question": question,
            "matched_results": matched_results,
            "web_result": web_result,
            "augmented_prompt": augmented_prompt,
            "answer": answer
        }
