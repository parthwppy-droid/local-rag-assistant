# Local RAG Assistant

A fully offline, privacy-first Q&A system that answers questions using
your own documents, powered by a local LLM (via Ollama).

## How it works
1. **Ingestion**: Documents are loaded, split into ~300-word chunks 
   (with overlap), and embedded into a vector database.
2. **Query**: A question is embedded the same way, matched against 
   stored chunks via cosine similarity, and the top matches are fed 
   into a prompt sent to a local LLM for generation.
3. **Fallback**: If local docs don't have the answer, it falls back 
   to live web search (Wikipedia/DuckDuckGo).

## Tech stack
- Python
- Ollama (Llama 3.2) for local LLM inference
- sentence-transformers for embeddings (with a TF-IDF fallback if unavailable)
- Custom JSON-based vector store with cosine similarity search
- Lightweight built-in HTTP server for the web UI

## Setup
1. Install [Ollama](https://ollama.com) and run `ollama pull llama3.2`
2. `pip install -r requirements.txt`
3. Add your documents to `sample_docs/`
4. Run `python web_app.py` and open `http://localhost:5000`

## Limitations
- Falls back to TF-IDF keyword matching if `sentence-transformers` isn't 
  installed (semantic matching won't work in this mode)
- Falls back to a rule-based answer engine if Ollama isn't reachable
- CPU inference can be slow on the first request per session

## Screenshots / Demo
https://github.com/user-attachments/assets/de7a7ab3-ce1f-452e-9f01-cd92f416e514
