import requests

class GitHubAgent:
    def __init__(self):
        self.repo = "microsoft/vscode"
        
    def get_top_issues(self, label="bug", limit=2, since=None):
        url = f"https://api.github.com/repos/{self.repo}/issues"
        params = {
            "state": "open", 
            "labels": label,
            "per_page": limit, 
            "sort": "created", 
            "direction": "desc"
        }
        if since:
            params["since"] = since
            
        try:
            r = requests.get(
                url, 
                headers={"Accept": "application/vnd.github.v3+json"}, 
                params=params, 
                timeout=5
            )
            if r.status_code == 200:
                return [{
                    "title": i['title'][:80], 
                    "comments": i['comments'], 
                    "url": i['html_url'], 
                    "created": i['created_at'][:10]
                } for i in r.json()]
        except Exception:
            pass
        return []
