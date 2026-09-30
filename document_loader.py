"""
Step 1 of Ingestion Phase: Document Loader
Reads text files (.txt, .md, .pdf) from a target folder.
"""
import os

class DocumentLoader:
    def __init__(self, docs_directory):
        self.docs_directory = docs_directory

    def load_documents(self):
        """Loads all supported documents from the target folder."""
        documents = []
        if not os.path.exists(self.docs_directory):
            print(f"⚠️ Warning: Directory '{self.docs_directory}' does not exist.")
            return documents

        for root, _, files in os.walk(self.docs_directory):
            for filename in files:
                if filename.endswith(('.txt', '.md', '.py', '.c', '.java', '.json')):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if content.strip():
                                documents.append({
                                    "filename": filename,
                                    "filepath": filepath,
                                    "content": content
                                })
                    except Exception as e:
                        print(f"❌ Error reading file {filename}: {e}")
        
        print(f"📄 Loaded {len(documents)} document(s) from '{self.docs_directory}'.")
        return documents
