import requests

class SocialAgent:
    def get_hn_discussions(self, query="VS Code"):
        url = f"https://hn.algolia.com/api/v1/search?query={query}&hitsPerPage=5"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return [{"title": h.get('title','')[:200], "points": h.get('points',0), 
                         "url": h.get('url','')} for h in response.json().get('hits',[])]
        except Exception:
            pass
        return []

    def get_reddit_posts(self, subreddit="vscode", limit=5):
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        headers = {'User-Agent': 'CodePulseBot/1.0'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                posts = []
                for child in response.json()['data']['children']:
                    d = child['data']
                    posts.append({"title": d['title'][:200], "score": d['score'],
                                 "num_comments": d['num_comments'],
                                 "url": f"https://reddit.com{d['permalink']}"})
                return posts
        except Exception:
            pass
        return []
