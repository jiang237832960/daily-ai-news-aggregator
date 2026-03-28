"""RSS/Atom feed crawler"""

import feedparser
from datetime import datetime
from typing import List
from email.utils import parsedate_to_datetime

from ..models import SourceType, RawContent
from .base import BaseCrawler, register_crawler


@register_crawler(SourceType.RSS)
class RSSCrawler(BaseCrawler):
    """Crawler for RSS/Atom feeds"""
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.RSS
    
    async def fetch(self, hours: int = 24) -> List[RawContent]:
        """Fetch content from RSS/Atom feed"""
        articles = []
        
        if not self.source.url:
            return articles
        
        response = await self._fetch_with_retry(self.source.url)
        if not response:
            return articles
        
        try:
            feed = feedparser.parse(response.text)
        except Exception:
            return articles
        
        for entry in feed.entries[:20]:
            try:
                published_at = self._parse_date(entry)
                
                if not self._is_within_time_window(published_at, hours):
                    continue
                
                article = RawContent(
                    url=self._get_entry_url(entry),
                    title=entry.get("title", ""),
                    content=entry.get("summary", "") or entry.get("description", ""),
                    author=entry.get("author", ""),
                    published_at=published_at
                )
                articles.append(article)
                
            except Exception:
                continue
        
        return articles
    
    def _parse_date(self, entry) -> datetime | None:
        """Parse date from entry"""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                from time import mktime
                return datetime.fromtimestamp(mktime(entry.published_parsed))
            except Exception:
                pass
        
        if hasattr(entry, "updated_parsed") and entry.updated_parsed:
            try:
                from time import mktime
                return datetime.fromtimestamp(mktime(entry.updated_parsed))
            except Exception:
                pass
        
        return None
    
    def _get_entry_url(self, entry) -> str:
        """Get URL from entry"""
        if hasattr(entry, "link"):
            return entry.link
        
        if hasattr(entry, "id"):
            return entry.id
        
        return ""
