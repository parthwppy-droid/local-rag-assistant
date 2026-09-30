import urllib.request
import urllib.parse
import json
import re

def clean_query_to_topic(query):
    # Remove quotes
    q = query.replace('"', '').replace("'", "")
    # Remove common question phrases
    patterns = [
        r'what does\s+(.*?)\s+actually stand for',
        r'what does\s+(.*?)\s+stand for',
        r'what is the full form of\s+(.*)',
        r'full form of\s+(.*)',
        r'what is\s+(.*)',
        r'who is\s+(.*)',
    ]
    for p in patterns:
        m = re.search(p, q, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return q.strip()

topic = clean_query_to_topic('What does "CAPTCHA" actually stand for?')
print("Extracted topic:", topic)

url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=1&explaintext=1&titles={urllib.parse.quote(topic)}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        pages = data.get('query', {}).get('pages', {})
        for pid, pinfo in pages.items():
            if pid != '-1' and 'extract' in pinfo:
                print("Wikipedia Page Title:", pinfo.get('title'))
                print("Extract:", pinfo.get('extract')[:300])
except Exception as e:
    print("Error:", e)
