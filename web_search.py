"""
Live Web Search Integration Module (Wikipedia Page Extract API + Fulltext API + Google News RSS)
Enables RAG to fetch real-time acronym expansions, definitions, trivia answers, world facts, and news.
"""
import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
import re

class LiveWebSearch:
    @staticmethod
    def extract_core_topic(query):
        """Extracts core topic or acronym from questions (e.g. What does CAPTCHA stand for -> CAPTCHA)."""
        q = query.replace('"', '').replace("'", "")
        patterns = [
            r'what does\s+(.*?)\s+(actually|really)?\s*stand for',
            r'what is the full form of\s+(.*)',
            r'full form of\s+(.*)',
            r'what is\s+(.*)',
            r'who is\s+(.*)',
            r'tell me about\s+(.*)',
            r'explain\s+(.*)'
        ]
        for p in patterns:
            m = re.search(p, q, re.IGNORECASE)
            if m:
                clean = m.group(1).strip()
                if clean:
                    return clean
        
        # Default cleanup
        clean_q = re.sub(r'[^\w\s]', '', q).strip()
        stop_words = ["who", "what", "where", "when", "why", "how", "is", "was", "are", "were", "the", "a", "an", "built", "did", "does", "give", "me", "tell", "about", "process", "for", "actually", "stand"]
        words = [w for w in clean_q.split() if w.lower() not in stop_words]
        return " ".join(words) if words else clean_q

    @classmethod
    def search_wikipedia_exact_page(cls, query):
        """Fetches introductory summary for the exact page title (Ideal for acronyms like CAPTCHA, NASA, HTML)."""
        try:
            topic = cls.extract_core_topic(query)
            url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=1&explaintext=1&titles={urllib.parse.quote(topic)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode('utf-8'))
                pages = data.get('query', {}).get('pages', {})
                for page_id, page_info in pages.items():
                    if page_id != '-1' and 'extract' in page_info:
                        extract = page_info['extract'].strip()
                        if extract and len(extract) > 20:
                            # Clean non-ASCII characters to avoid CP1252 Windows console crashes
                            clean_extract = extract[:900].encode('ascii', 'ignore').decode('ascii')
                            title = page_info.get('title', topic)
                            return f"• **{title}**: {clean_extract}"
        except Exception:
            pass
        return None

    @staticmethod
    def search_wikipedia_fulltext(query):
        """Searches Wikipedia Fulltext Search API for trivia riddles and complex questions."""
        try:
            url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                results = data.get('query', {}).get('search', [])
                
                output_snippets = []
                for idx, r in enumerate(results[:3], 1):
                    title = r.get('title', '')
                    snippet = re.sub(r'<[^>]+>', '', r.get('snippet', '')).strip()
                    if title and snippet:
                        clean_snip = snippet.encode('ascii', 'ignore').decode('ascii')
                        output_snippets.append(f"• **{title}**: {clean_snip}")
                
                if output_snippets:
                    return "\n\n".join(output_snippets)
        except Exception:
            pass
        return None

    @staticmethod
    def fetch_google_news(topic="latest news"):
        """Fetches live top news headlines from Google News RSS feed."""
        try:
            clean_topic = re.sub(r'^(give me|show me|tell me|get|find|what is the|what are the)\s+', '', topic.strip(), flags=re.IGNORECASE)
            is_india = "india" in clean_topic.lower()
            search_query = re.sub(r'(latest news of|latest news in|news of|news about|news in|latest news|news|headlines)', '', clean_topic, flags=re.IGNORECASE).strip()

            if not search_query or search_query.lower() in ["india", ""]:
                if is_india or "india" in topic.lower():
                    rss_url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
                else:
                    rss_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
            else:
                encoded_q = urllib.parse.quote(clean_topic)
                gl_param = "IN" if is_india else "US"
                rss_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=en-{gl_param}&gl={gl_param}&ceid={gl_param}:en"

            req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=5) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)

                items = root.findall('.//item')
                news_headlines = []
                for idx, item in enumerate(items[:6], 1):
                    title = item.find('title')
                    pub_date = item.find('pubDate')
                    
                    t_text = title.text if title is not None else ""
                    d_text = pub_date.text[:16] if pub_date is not None else ""
                    
                    if t_text:
                        clean_t = t_text.encode('ascii', 'ignore').decode('ascii')
                        news_headlines.append(f"{idx}. {clean_t} ({d_text})")

                if news_headlines:
                    return "\n".join(news_headlines)
        except Exception:
            pass
        return None

    @classmethod
    def live_search(cls, query):
        """Fetches live search results or news for any query."""
        q_lower = query.lower()

        # 1. News query -> Google News RSS
        if any(w in q_lower for w in ["news", "headline", "headlines", "trending news", "latest news", "breaking news"]):
            news_res = cls.fetch_google_news(query)
            if news_res:
                return {"source": "Google News Live RSS Feed", "text": news_res}

        # 2. Acronym / Definition / Exact Page query -> Wikipedia Exact Page Extract API
        wiki_exact = cls.search_wikipedia_exact_page(query)
        if wiki_exact:
            return {"source": "Wikipedia Page Index", "text": wiki_exact}

        # 3. Wikipedia Fulltext Search API (Resolves complex trivia riddles)
        wiki_full = cls.search_wikipedia_fulltext(query)
        if wiki_full:
            return {"source": "Wikipedia Knowledge Base", "text": wiki_full}

        return None
