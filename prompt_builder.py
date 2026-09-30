"""
Step 4 of Query Phase: Prompt Builder
Combines retrieved relevant chunks with the user's question to build an augmented context prompt.
Distinguishes between document queries, general questions, and greetings.
"""

class PromptBuilder:
    @staticmethod
    def build_augmented_prompt(question, matched_results, similarity_threshold=0.50):
        """
        Formats retrieved top-K chunks into a clean context prompt.
        Only attaches document context if the similarity score meets the relevance threshold (> 0.50).
        """
        # Filter chunks that pass minimum similarity threshold
        relevant_chunks = [res for res in matched_results if res["score"] >= similarity_threshold]

        if not relevant_chunks:
            context_str = "No specific local document context found for this query."
        else:
            context_blocks = []
            for i, item in enumerate(relevant_chunks, start=1):
                chunk = item["chunk"]
                score = item["score"]
                block = f"--- [Local Document Context {i} | Source: {chunk['source']} | Relevance: {score:.3f}] ---\n{chunk['text']}"
                context_blocks.append(block)
            context_str = "\n\n".join(context_blocks)

        augmented_prompt = f"""You are a helpful, intelligent AI assistant.
Answer the user's question clearly, thoroughly, and accurately.

Instruction:
- If the question is a greeting or casual conversation (e.g., "hi", "how are you"), respond naturally and warmly.
- If the provided Local Document Context below contains relevant information, prioritize using it to answer.
- If the document context is not relevant or does not fully answer the question, use your general AI knowledge to answer completely.

Local Document Context:
====================
{context_str}
====================

User Question: {question}

Answer:"""

        return augmented_prompt
