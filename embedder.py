"""
Step 3 of Ingestion Phase & Step 2 of Query Phase: Vector Embedder

Primary path: SentenceTransformers (real semantic embeddings).
Fallback path (only used if sentence-transformers isn't installed): a fitted
TF-IDF vectorizer over the actual ingestion corpus. This is NOT semantic —
it only matches on shared words — so it is clearly logged as a fallback,
not silently swapped in.
"""
import math
import re
import json
import os

class VectorEmbedder:
    def __init__(self, model_name="all-MiniLM-L6-v2", vocab_path=None):
        self.model_name = model_name
        self.model = None
        self.vocab_path = vocab_path
        self.vocabulary = {}   # word -> index, fitted from the ingestion corpus
        self.idf = {}          # word -> inverse-document-frequency weight
        self._init_model()
        self.using_semantic_model = self.model is not None

        if not self.using_semantic_model:
            print("⚠️  'sentence-transformers' not installed — using a TF-IDF keyword")
            print("    fallback instead of real semantic embeddings. This fallback only")
            print("    matches shared WORDS, not meaning (e.g. 'car' won't match 'automobile').")
            print("    For real embeddings run: pip install sentence-transformers --break-system-packages")
            if self.vocab_path:
                self._load_vocab()

    def _init_model(self):
        """Initializes SentenceTransformers if installed."""
        try:
            from sentence_transformers import SentenceTransformer
            print(f"🔄 Loading local embedding model '{self.model_name}'...")
            self.model = SentenceTransformer(self.model_name)
            print(f"✅ Local embedding model '{self.model_name}' loaded successfully!")
        except Exception:
            self.model = None

    def embed_text(self, text):
        """Embeds a single string (e.g. a user question) into a vector of floats."""
        if self.model:
            return self.model.encode(text, convert_to_numpy=True).tolist()
        if not self.vocabulary:
            print("⚠️  No fitted TF-IDF vocabulary yet — run ingestion before querying.")
        return self._tfidf_vectorize(text)

    def embed_chunks(self, chunks):
        """Embeds a list of chunk objects (the ingestion corpus)."""
        print(f"🔢 Generating vector embeddings for {len(chunks)} chunk(s)...")
        texts = [c["text"] for c in chunks]

        if self.model:
            embeddings = self.model.encode(texts, convert_to_numpy=True).tolist()
        else:
            # Fit the TF-IDF vocabulary + IDF weights on THIS corpus, then vectorize.
            self._fit(texts)
            embeddings = [self._tfidf_vectorize(t) for t in texts]

        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i]

        print(f"✅ Embeddings generated. Vector dimension: {len(embeddings[0]) if embeddings else 0}")
        return chunks

    def _fit(self, texts):
        """
        Builds a real vocabulary and IDF weight table from the ingestion corpus.
        Replaces the old hashed-bucket approach, which could silently collide
        unrelated words into the same vector slot.
        """
        doc_freq = {}
        n_docs = len(texts) or 1
        vocab_set = set()
        for t in texts:
            words = set(re.findall(r'\w+', t.lower()))
            vocab_set.update(words)
            for w in words:
                doc_freq[w] = doc_freq.get(w, 0) + 1

        vocab_list = sorted(vocab_set)
        self.vocabulary = {w: i for i, w in enumerate(vocab_list)}
        # Standard smoothed IDF: log((N+1)/(df+1)) + 1
        self.idf = {w: math.log((n_docs + 1) / (doc_freq[w] + 1)) + 1 for w in vocab_list}

        print(f"📚 Fitted TF-IDF vocabulary: {len(self.vocabulary)} unique word(s) from {n_docs} chunk(s).")
        if self.vocab_path:
            self._save_vocab()

    def _tfidf_vectorize(self, text):
        """
        Real TF-IDF vector using the fitted vocabulary. Words not seen during
        fitting are ignored (a known, expected TF-IDF limitation) rather than
        hashed into a random, possibly-colliding slot.
        """
        if not self.vocabulary:
            return [0.0]

        vec = [0.0] * len(self.vocabulary)
        words = re.findall(r'\w+', text.lower())
        if not words:
            return vec

        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1

        for word, count in freq.items():
            idx = self.vocabulary.get(word)
            if idx is None:
                continue  # out-of-vocabulary word
            tf = count / len(words)
            vec[idx] = tf * self.idf.get(word, 1.0)

        norm = math.sqrt(sum(x * x for x in vec)) + 1e-9
        return [round(x / norm, 6) for x in vec]

    def _save_vocab(self):
        if not self.vocab_path:
            return
        try:
            with open(self.vocab_path, "w", encoding="utf-8") as f:
                json.dump({"vocabulary": self.vocabulary, "idf": self.idf}, f)
        except Exception as e:
            print(f"⚠️ Could not save TF-IDF vocabulary: {e}")

    def _load_vocab(self):
        if self.vocab_path and os.path.exists(self.vocab_path):
            try:
                with open(self.vocab_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.vocabulary = data.get("vocabulary", {})
                self.idf = data.get("idf", {})
                if self.vocabulary:
                    print(f"📚 Loaded existing TF-IDF vocabulary ({len(self.vocabulary)} words).")
            except Exception:
                pass
