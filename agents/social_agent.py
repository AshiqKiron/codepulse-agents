import requests

class SocialAgent:
    def get_hn_discussions(self, query="vscode", limit=2):
        url = f"https://hn.algolia.com/api/v1/search?query={query}&hitsPerPage={limit}"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                return [{
                    "title": h.get('title','')[:80], 
                    "points": h.get('points',0),
                    "created": h.get('created_at_i',0)
                } for h in r.json().get('hits',[])]
        except Exception:
            pass
        return []
