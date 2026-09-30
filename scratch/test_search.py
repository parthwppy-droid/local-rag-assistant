import urllib.request
import urllib.parse
import json
import re

query = "Which ancient wonder of the world was destroyed by an earthquake"
url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json"

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode('utf-8'))
        results = data.get('query', {}).get('search', [])
        print("Wikipedia Search Results Count:", len(results))
        for r in results[:4]:
            snippet = re.sub(r'<[^>]+>', '', r.get('snippet', ''))
            print(f"Title: {r.get('title')}")
            print(f"Snippet: {snippet}\n")
except Exception as e:
    print("Error:", e)
