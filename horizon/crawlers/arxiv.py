"""ArXiv crawler"""

import feedparser
from datetime import datetime
from typing import List

from ..models import SourceType, RawContent
from .base import BaseCrawler, register_crawler


@register_crawler(SourceType.ARXIV)
class ArxivCrawler(BaseCrawler):
    """Crawler for ArXiv RSS feeds"""
    
    ARXIV_API = "https://export.arxiv.org/api/query?"
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.ARXIV
    
    async def fetch(self, hours: int = 24) -> List[RawContent]:
        """Fetch latest papers from ArXiv"""
        articles = []
        
        search_query = self.source.url or "cat:cs.AI"
        url = f"{self.ARXIV_API}search_query={search_query}&max_results=20&sortBy=submittedDate&sortOrder=descending"
        
        response = await self._fetch_with_retry(url)
        if not response:
            return articles
        
        try:
            feed = feedparser.parse(response.text)
            
            for entry in feed.entries[:20]:
                try:
                    published_at = datetime(*entry.published_parsed[:6])
                    
                    if not self._is_within_time_window(published_at, hours):
                        continue
                    
                    article = RawContent(
                        url=entry.get("id", ""),
                        title=entry.get("title", "").replace("\n", " "),
                        content=entry.get("summary", "").replace("\n", " "),
                        author=", ".join([a.get("name", "") for a in entry.get("authors", [])]),
                        published_at=published_at
                    )
                    articles.append(article)
                    
                except Exception:
                    continue
                
        except Exception:
            pass
        
        return articles
