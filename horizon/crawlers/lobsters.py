"""Lobsters crawler"""

from datetime import datetime
from typing import List

from ..models import SourceType, RawContent
from .base import BaseCrawler, register_crawler


@register_crawler(SourceType.LOBSTERS)
class LobstersCrawler(BaseCrawler):
    """Crawler for Lobsters"""
    
    LOBSTERS_API = "https://lobste.rs"
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.LOBSTERS
    
    async def fetch(self, hours: int = 24) -> List[RawContent]:
        """Fetch hot stories from Lobsters"""
        articles = []
        
        response = await self._fetch_with_retry(f"{self.LOBSTERS_API}/hot.json")
        if not response:
            return articles
        
        try:
            stories = response.json()
            
            for story in stories[:20]:
                published_at = None
                if story.get("created_at"):
                    published_at = datetime.fromisoformat(
                        story["created_at"].replace("Z", "+00:00")
                    )
                
                if not self._is_within_time_window(published_at, hours):
                    continue
                
                article = RawContent(
                    url=story.get("url", "") or f"{self.LOBSTERS_API}/s/{story.get('short_id', '')}",
                    title=story.get("title", ""),
                    content=story.get("description", ""),
                    author=story.get("submitter_user", {}).get("username", ""),
                    published_at=published_at,
                    engagement=self._extract_engagement(story)
                )
                articles.append(article)
                
        except Exception:
            pass
        
        return articles
    
    def _extract_engagement(self, story: dict) -> dict:
        """Extract engagement metrics"""
        return {
            "comments": story.get("comment_count", 0),
            "likes": story.get("score", 0),
            "shares": 0
        }
