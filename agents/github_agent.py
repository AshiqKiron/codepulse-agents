import requests

class GitHubAgent:
    def __init__(self):
        self.repo = "microsoft/vscode"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        
    def get_top_issues(self, label="bug", limit=3):
        url = f"https://api.github.com/repos/{self.repo}/issues"
        params = {
            "state": "open", "labels": label,
            "per_page": limit, "sort": "comments", "direction": "desc"
        }
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                return [{
                    "title": issue['title'][:150],  # Truncate title
                    "comments": issue['comments'],
                    "url": issue['html_url']
                } for issue in response.json()]
        except Exception:
            pass
        return []
