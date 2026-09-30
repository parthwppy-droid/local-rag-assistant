"""
Step 5 of Query Phase: Universal Local AI Generator (ChatGPT/Claude Style)
Handles:
1. Conversational Chat Memory
2. Local Document Retrieval (RAG)
3. Universal Super Knowledge Engine (Covers all 25+ domains)
"""
import requests
import json
import re
from world_knowledge import UniversalKnowledgeEngine
from super_knowledge import SuperKnowledgeEngine

class LocalLLM:
    def __init__(self, ollama_url="http://localhost:11434", default_model=None):
        self.ollama_url = ollama_url
        self.default_model = default_model
        self.chat_history = []

    def get_available_model(self):
        """Auto-detects active models in Ollama."""
        try:
            res = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            if res.status_code == 200:
                models = res.json().get("models", [])
                if models:
                    return models[0]["name"]
        except Exception:
            pass
        return None

    def generate_answer(self, prompt, raw_question, matched_chunks=None, web_result=None):
        """
        Generates an answer via the local Ollama model. Falls back to the
        keyword-matched knowledge engine ONLY when Ollama is unreachable —
        that fallback is logged loudly so it's never mistaken for real
        model output.
        """
        model_name = self.default_model or self.get_available_model()

        if model_name:
            endpoint = f"{self.ollama_url}/api/generate"

            full_prompt = prompt
            if web_result:
                full_prompt = f"Web Search Context ({web_result['source']}): {web_result['text']}\n\nQuestion: {raw_question}\nAnswer:"

            # Fold in recent conversation turns so multi-turn context actually
            # reaches the model (previously collected but never sent).
            if self.chat_history:
                history_text = "\n".join(
                    f"{turn['role'].capitalize()}: {turn['content']}"
                    for turn in self.chat_history[-6:]  # last 3 exchanges
                )
                full_prompt = f"Previous conversation:\n{history_text}\n\n{full_prompt}"

            payload = {
                "model": model_name,
                "prompt": full_prompt,
                "stream": False
            }

            try:
                print(f"[Ollama] Generating with model '{model_name}'... "
                      f"(first response can take 1-2+ min on CPU while the model loads)")
                response = requests.post(endpoint, json=payload, timeout=300)

                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("response", "No response generated.")
                    self.chat_history.append({"role": "user", "content": raw_question})
                    self.chat_history.append({"role": "assistant", "content": answer})
                    return answer
            except Exception as e:
                print(f"[LLM Note] Local server unreachable: {e}")

        # Fallback path — Ollama is down or no model is pulled yet.
        print("⚠️  [FALLBACK MODE] Ollama unavailable — answering with the keyword-matched")
        print("    knowledge engine instead of real model generation. Run `ollama serve` /")
        print("    pull a model for actual LLM answers.")
        answer = self._universal_knowledge_engine(raw_question, prompt, matched_chunks, web_result)
        self.chat_history.append({"role": "user", "content": raw_question})
        self.chat_history.append({"role": "assistant", "content": answer})
        return answer

    def _universal_knowledge_engine(self, question, prompt, matched_chunks, web_result=None):
        """
        Universal resolver that answers ANY question across all domains.
        """
        clean_q = re.sub(r'[^\w\s]', '', question.strip().lower())

        # 1. Greetings & Chit-chat
        greetings = ["hi", "hello", "hey", "how are you", "who are you", "what can you do", "good morning", "good evening"]
        if clean_q in greetings or any(g in clean_q for g in ["how are you", "who are you", "hello", "hi there"]):
            if "how are you" in clean_q:
                return "I'm doing great! I am your AI assistant. Ask me any question!"
            elif "who are you" in clean_q or "what can you do" in clean_q:
                return "I am an AI Assistant. I can answer any question about science, history, coding, finance, travel, fitness, legal rights, movies, or read your local files!"
            else:
                return "Hello! How can I help you today? Ask me any question!"

        # 2. Check Multi-Domain Super Knowledge
        domain_answer = SuperKnowledgeEngine.resolve_domain_query(question)
        if domain_answer:
            return domain_answer

        # 3. Local Document Context Query (High relevance match threshold > 0.70)
        if matched_chunks and len(matched_chunks) > 0 and matched_chunks[0]["score"] >= 0.70:
            top_chunk = matched_chunks[0]["chunk"]
            score = matched_chunks[0]["score"]
            return f"📄 [Answer from Local Document: {top_chunk['source']} | Score: {score:.2f}]\n\n{top_chunk['text']}"

        # 4. Procedural / Process Questions (Passport, Visa, License, Registration, How-to)
        if any(kw in clean_q for kw in ["passport", "visa", "process for", "procedure for", "how to apply", "steps to get", "how do i get"]):
            return self._generate_procedural_answer(clean_q)

        # 5. Web Search Result (if available)
        if web_result:
            return f"🌐 [Live Knowledge Search Result from {web_result['source']}]:\n\n{web_result['text']}"

        # 6. Universal World Knowledge Engine (Wikipedia, DuckDuckGo, Google News)
        return UniversalKnowledgeEngine.answer_anything(question)

    def _generate_procedural_answer(self, query):
        """Generates step-by-step procedural guides for official processes."""
        if "passport" in query:
            return """📘 **Official Step-by-Step Passport Application Process (India / Passport Seva)**:

1. **Online Registration**: Visit `passportindia.gov.in` and register an account.
2. **Fill Application Form**: Click on "Apply for Fresh Passport" and fill personal details.
3. **Pay Fee & Book Appointment**: Pay fee online and select nearest PSK / POPSK slot.
4. **Visit PSK for Verification**: Bring original documents (Aadhaar, DOB proof) and complete biometrics.
5. **Police Verification**: Local police verify address and identity details.
6. **Passport Dispatch**: Delivered via Speed Post to your registered address."""

        elif "visa" in query:
            return """🛂 **Step-by-Step Visa Application Process**:

1. Determine Visa Type (Tourist, Student, Work, Business).
2. Prepare Passport (6 months validity), photos, bank statements, itinerary.
3. Complete online embassy/VFS application form.
4. Book appointment slot at VFS/Embassy.
5. Attend interview/biometrics and collect stamped passport."""

        else:
            return f"📋 **Step-by-Step Process for {query}**:\n1. Access official government portal.\n2. Fill application form & upload identity proofs.\n3. Complete verification & pay fee."
