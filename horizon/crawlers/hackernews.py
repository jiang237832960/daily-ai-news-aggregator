"""HackerNews crawler with Scrapling content fetching"""

import asyncio
import re
from datetime import datetime
from typing import List

from ..models import SourceType, RawContent, Engagement
from .base import BaseCrawler, register_crawler
from ..fetcher import ContentFetcher


@register_crawler(SourceType.HACKERNEWS)
class HackerNewsCrawler(BaseCrawler):
    """Crawler for HackerNews with Scrapling content fetching"""
    
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
        
        fetcher = ContentFetcher()
        
        for story_id in story_ids[:10]:
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
                
                external_url = story.get("url", "")
                content = ""
                
                if external_url:
                    content, error = await fetcher.fetch(external_url)
                
                if not content and story.get("text"):
                    content = self._clean_html(story["text"])
                
                article = RawContent(
                    url=external_url or f"https://news.ycombinator.com/item?id={story_id}",
                    title=story.get("title", ""),
                    content=content,
                    author=story.get("by", ""),
                    published_at=published_at,
                    engagement=Engagement(
                        comments=story.get("descendants", 0),
                        likes=0,
                        shares=story.get("score", 0)
                    )
                )
                articles.append(article)
                
            except Exception:
                continue
        
        await fetcher.close()
        return articles
    
    def _clean_html(self, text: str) -> str:
        """Clean HTML text"""
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _extract_engagement(self, story: dict) -> dict:
        """Extract engagement metrics from story"""
        return {
            "comments": story.get("descendants", 0),
            "likes": 0,
            "shares": story.get("score", 0)
        }
