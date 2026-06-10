import requests

class GitHubAgent:
    def __init__(self):
        self.repo = "microsoft/vscode"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        
    def get_top_issues(self, label="bug", limit=5):
        url = f"https://api.github.com/repos/{self.repo}/issues"
        params = {
            "state": "open", "labels": label,
            "per_page": limit, "sort": "comments", "direction": "desc"
        }
        response = requests.get(url, headers=self.headers, params=params, timeout=10)
        if response.status_code == 200:
            return [{
                "title": issue['title'][:200],
                "comments": issue['comments'],
                "url": issue['html_url'],
                "created_at": issue['created_at']
            } for issue in response.json()]
        return []
