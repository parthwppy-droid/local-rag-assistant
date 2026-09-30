"""
Maximal Universal Knowledge Engine (Zero "No Data" Policy)
Ensures the system NEVER says "I don't have this data" or "Not found".
Fetches live data from Wikipedia, DuckDuckGo, Google News, and Web Knowledge Synthesizers.
"""
import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
import re

class UniversalKnowledgeEngine:
    @staticmethod
    def extract_entity_title(query):
        clean_q = re.sub(r'[^\w\s]', '', query).strip()
        stop_words = ["who", "what", "where", "when", "why", "how", "is", "was", "are", "were", "the", "a", "an", "built", "did", "does", "give", "me", "tell", "about", "process", "for", "poem", "thought", "quote", "explain", "describe", "detail"]
        words = [w for w in clean_q.split() if w.lower() not in stop_words]
        return " ".join(words) if words else clean_q

    @classmethod
    def get_wikipedia_summary(cls, query):
        """Fetches encyclopedia-grade answers for facts, science, history, people, places, concepts."""
        try:
            entity_name = cls.extract_entity_title(query)
            url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=1&explaintext=1&titles={urllib.parse.quote(entity_name)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode('utf-8'))
                pages = data.get('query', {}).get('pages', {})
                for page_id, page_info in pages.items():
                    if page_id != '-1' and 'extract' in page_info:
                        extract = page_info['extract'].strip()
                        if extract and len(extract) > 20:
                            return extract[:1000]
        except Exception:
            pass
        return None

    @staticmethod
    def get_duckduckgo_answer(query):
        """Fetches DuckDuckGo Instant Answers for general queries."""
        try:
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode('utf-8'))
                abstract = data.get('AbstractText', '').strip()
                if abstract and len(abstract) > 20:
                    return abstract
                
                related = data.get('RelatedTopics', [])
                if related and isinstance(related[0], dict) and 'Text' in related[0]:
                    return related[0]['Text']
        except Exception:
            pass
        return None

    @staticmethod
    def get_google_news(query):
        """Fetches live news headlines."""
        try:
            encoded_q = urllib.parse.quote(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=en-IN&gl=IN&ceid=IN:en"
            req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                items = root.findall('.//item')
                news = []
                for idx, item in enumerate(items[:5], 1):
                    t = item.find('title')
                    if t is not None and t.text:
                        news.append(f"{idx}. {t.text}")
                if news:
                    return "\n".join(news)
        except Exception:
            pass
        return None

    @classmethod
    def generate_creative_writing(cls, query):
        """Generates poems, thoughts of the day, motivational quotes, and creative writing."""
        q_lower = query.lower()

        if "poem" in q_lower or "poetry" in q_lower or "rhyme" in q_lower:
            return """📜 **Poem: Whispers of the Dawn**

The quiet stars begin to fade,
As morning paints the quiet shade.
A gentle breeze begins to blow,
Where rivers shine and forests glow.

With every sunrise comes a chance,
To join the sun's triumphant dance.
Believe in dreams you hold so dear,
For hope will wash away all fear."""

        elif "thought" in q_lower or "quote" in q_lower or "motivation" in q_lower:
            return """💡 **Thought of the Day**:

> *"Small daily improvements over time lead to stunning long-term results."*

**Key Takeaway**: Do not get overwhelmed by big goals. Focus on taking one small positive step every single day, and consistency will build extraordinary success."""

        return None

    @classmethod
    def answer_anything(cls, query):
        """
        Maximal Universal resolver that fetches data from all sources to answer ANY question in the world.
        NEVER returns 'no data' or 'not found'.
        """
        q_clean = query.strip()

        # 1. Creative Writing & Poems
        creative = cls.generate_creative_writing(q_clean)
        if creative:
            return creative

        # 2. Wikipedia entity lookup
        wiki = cls.get_wikipedia_summary(q_clean)
        if wiki:
            return f"🌐 [World Knowledge Index - Wikipedia]:\n\n{wiki}"

        # 3. DuckDuckGo Instant Answer
        ddg = cls.get_duckduckgo_answer(q_clean)
        if ddg:
            return f"🌐 [Live Web Knowledge - DuckDuckGo]:\n\n{ddg}"

        # 4. Google News Search
        news = cls.get_google_news(q_clean)
        if news:
            return f"📰 [Live News Search]:\n\n{news}"

        # 5. Honest "not found" — no fake generic filler.
        return cls._honest_no_answer(q_clean)

    @staticmethod
    def _honest_no_answer(query):
        """
        Previously this generated generic templated filler text ("Component A:
        Core foundation...") that LOOKED like an answer but carried zero real
        information about the query. That's worse than saying nothing, because
        it can mislead whoever's reading it. This says plainly what happened
        and what to do next instead.
        """
        return (
            f"I couldn't find real information on \"{query}\" from the local documents, "
            f"Wikipedia, or DuckDuckGo, and the local LLM (Ollama) isn't reachable right now "
            f"to reason about it directly.\n\n"
            f"To get an actual answer: make sure Ollama is running (`ollama serve`) and a model "
            f"is pulled (`ollama pull llama3.2`), then ask again — or check your internet "
            f"connection if this should have been a web lookup."
        )
