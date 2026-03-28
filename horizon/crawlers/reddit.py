"""Reddit crawler"""

import base64
from datetime import datetime, timedelta
from typing import List, Optional

from ..models import SourceType, RawContent
from .base import BaseCrawler, register_crawler


@register_crawler(SourceType.REDDIT)
class RedditCrawler(BaseCrawler):
    """Crawler for Reddit"""
    
    REDDIT_API = "https://www.reddit.com"
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.REDDIT
    
    async def fetch(self, hours: int = 24) -> List[RawContent]:
        """Fetch posts from subreddit"""
        articles = []
        
        subreddit = self.source.url or "machinelearning"
        url = f"{self.REDDIT_API}/{subreddit}/hot.json?limit=25"
        
        headers = {}
        auth_config = self.source.auth_config
        if auth_config.get("client_id") and auth_config.get("client_secret"):
            auth_string = f"{auth_config['client_id']}:{auth_config['client_secret']}"
            headers["Authorization"] = f"Basic {base64.b64encode(auth_string.encode()).decode()}"
        
        response = await self._fetch_with_retry(
            url,
            headers=headers
        )
        if not response:
            return articles
        
        try:
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            
            for post in posts:
                post_data = post.get("data", {})
                
                published_at = datetime.fromtimestamp(post_data.get("created_utc", 0))
                
                if not self._is_within_time_window(published_at, hours):
                    continue
                
                article = RawContent(
                    url=f"https://reddit.com{post_data.get('permalink', '')}",
                    title=post_data.get("title", ""),
                    content=post_data.get("selftext", ""),
                    author=post_data.get("author", ""),
                    published_at=published_at,
                    engagement=self._extract_engagement(post_data)
                )
                articles.append(article)
                
        except Exception:
            pass
        
        return articles
    
    def _extract_engagement(self, post_data: dict) -> dict:
        """Extract engagement metrics from post"""
        return {
            "comments": post_data.get("num_comments", 0),
            "likes": post_data.get("score", 0),
            "shares": post_data.get("num_crossposts", 0)
        }
