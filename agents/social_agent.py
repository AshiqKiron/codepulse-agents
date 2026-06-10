import requests

class SocialAgent:
    def get_hn_discussions(self, query="VS Code"):
        """Search Hacker News via Algolia API"""
        url = f"https://hn.algolia.com/api/v1/search?query={query}&hitsPerPage=5"
        response = requests.get(url)
        if response.status_code == 200:
            return [{
                "title": hit.get('title', ''),
                "points": hit.get('points', 0),
                "url": hit.get('url', '')
            } for hit in response.json().get('hits', [])]
        return []

    def get_reddit_posts(self, subreddit="vscode", limit=5):
        """Scrape Reddit without API key using .json endpoint"""
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        headers = {'User-Agent': 'CodePulseBot/1.0'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            posts = []
            for post in response.json()['data']['children']:
                data = post['data']
                posts.append({
                    "title": data['title'],
                    "score": data['score'],
                    "num_comments": data['num_comments'],
                    "url": f"https://reddit.com{data['permalink']}"
                })
            return posts
        return []
