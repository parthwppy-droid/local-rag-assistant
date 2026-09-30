"""
Interactive Main Entry Point for Local RAG System
"""
import sys
import os
import io

# Ensure UTF-8 output formatting for Windows consoles
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from rag_pipeline import LocalRAGPipeline

def print_banner():
    print("""
============================================================
[LOCAL RAG SYSTEM] Retrieval-Augmented Generation
============================================================
Flow Architecture:
Phase 1: Documents -> Chunking -> Embedding -> Vector DB
Phase 2: Question  -> Embedding -> Search -> Prompt -> LLM
============================================================
""")

def main():
    print_banner()
    
    docs_dir = os.path.join(os.path.dirname(__file__), "sample_docs")
    db_path = os.path.join(os.path.dirname(__file__), "vector_store.json")

    pipeline = LocalRAGPipeline(docs_dir=docs_dir, db_path=db_path)

    # Automatically run Ingestion if DB doesn't exist
    if not os.path.exists(db_path) or len(pipeline.vector_db.chunks) == 0:
        print("Vector DB not found or empty. Running Phase 1 Ingestion first...")
        pipeline.run_ingestion()
    else:
        print(f"[OK] Found existing Vector DB with {len(pipeline.vector_db.chunks)} indexed chunk(s).")

    # Command line query mode
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        result = pipeline.query(question)
        print("\n" + "="*60)
        print("LOCAL LLM RESPONSE:")
        print("="*60)
        print(result["answer"])
        return

    # Interactive mode
    print("\nEnter a question to query your local documents (type 'exit' to quit):")
    while True:
        try:
            user_input = input("\nAsk a Question > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting Local RAG System. Goodbye!")
                break
            if user_input.lower() == "reindex":
                pipeline.run_ingestion()
                continue

            result = pipeline.query(user_input)
            print("\n" + "="*60)
            print("LOCAL LLM RESPONSE:")
            print("="*60)
            print(result["answer"])
            print("="*60)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break

if __name__ == "__main__":
    main()
