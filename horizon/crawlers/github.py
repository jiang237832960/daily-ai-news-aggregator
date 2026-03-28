"""GitHub crawler"""

from datetime import datetime
from typing import List

from ..models import SourceType, RawContent
from .base import BaseCrawler, register_crawler


@register_crawler(SourceType.GITHUB)
class GitHubCrawler(BaseCrawler):
    """Crawler for GitHub"""
    
    GITHUB_API = "https://api.github.com"
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.GITHUB
    
    async def fetch(self, hours: int = 24) -> List[RawContent]:
        """Fetch latest releases from GitHub"""
        articles = []
        
        repo = self.source.url or "MicheleML/horizon"
        url = f"{self.GITHUB_API}/repos/{repo}/releases"
        
        headers = {}
        auth_config = self.source.auth_config
        if auth_config.get("token"):
            headers["Authorization"] = f"Bearer {auth_config['token']}"
        
        response = await self._fetch_with_retry(url, headers=headers)
        if not response:
            return articles
        
        try:
            releases = response.json()
            if not isinstance(releases, list):
                return articles
            
            for release in releases[:20]:
                published_at = datetime.fromisoformat(
                    release.get("published_at", "").replace("Z", "+00:00")
                )
                
                if not self._is_within_time_window(published_at, hours):
                    continue
                
                article = RawContent(
                    url=release.get("html_url", ""),
                    title=release.get("name", "") or release.get("tag_name", ""),
                    content=release.get("body", ""),
                    author=release.get("author", {}).get("login", ""),
                    published_at=published_at
                )
                articles.append(article)
                
        except Exception:
            pass
        
        return articles
