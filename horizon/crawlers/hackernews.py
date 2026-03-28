"""HackerNews crawler"""

from datetime import datetime
from typing import List

from ..models import SourceType, RawContent
from .base import BaseCrawler, register_crawler


@register_crawler(SourceType.HACKERNEWS)
class HackerNewsCrawler(BaseCrawler):
    """Crawler for HackerNews"""
    
    HN_API_URL = "https://hacker-news.firebaseio.com/v0"
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.HACKERNEWS
    
    async def fetch(self, hours: int = 24) -> List[RawContent]:
        """Fetch top stories from HackerNews"""
        articles = []
        
        response = await self._fetch_with_retry(f"{self.HN_API_URL}/topstories.json")
        if not response:
            return articles
        
        story_ids = response.json()[:30]
        
        for story_id in story_ids:
            try:
                story_response = await self._fetch_with_retry(
                    f"{self.HN_API_URL}/item/{story_id}.json"
                )
                if not story_response:
                    continue
                
                story = story_response.json()
                if not story:
                    continue
                
                published_at = None
                if story.get("time"):
                    published_at = datetime.fromtimestamp(story["time"])
                
                if not self._is_within_time_window(published_at, hours):
                    continue
                
                article = RawContent(
                    url=story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                    title=story.get("title", ""),
                    content=story.get("text", ""),
                    author=story.get("by", ""),
                    published_at=published_at,
                    engagement=self._extract_engagement(story)
                )
                articles.append(article)
                
            except Exception:
                continue
        
        return articles
    
    def _extract_engagement(self, story: dict) -> dict:
        """Extract engagement metrics from story"""
        return {
            "comments": story.get("descendants", 0),
            "likes": 0,
            "shares": story.get("score", 0)
        }
