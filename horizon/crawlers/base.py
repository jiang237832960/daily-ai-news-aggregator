"""Base crawler class"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional

import httpx

from ..models import Source, SourceType, RawContent


class BaseCrawler(ABC):
    """Base class for all crawlers"""
    
    def __init__(self, source: Source):
        self.source = source
        self.client: Optional[httpx.AsyncClient] = None
    
    @property
    @abstractmethod
    def source_type(self) -> SourceType:
        """Return the source type this crawler handles"""
        pass
    
    def supports(self, source_type: SourceType) -> bool:
        """Check if this crawler supports the given source type"""
        return self.source_type == source_type
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=self.source.timeout,
                follow_redirects=True
            )
        return self.client
    
    async def _fetch_with_retry(
        self,
        url: str,
        method: str = "GET",
        **kwargs
    ) -> Optional[httpx.Response]:
        """Fetch URL with retry logic"""
        client = await self._get_client()
        
        for attempt in range(self.source.retry_times):
            try:
                response = await client.request(method, url, **kwargs)
                if response.status_code == 200:
                    return response
                elif response.status_code in (429, 500, 502, 503, 504):
                    await self._handle_rate_limit(attempt)
                else:
                    return response
            except httpx.TimeoutException:
                if attempt == self.source.retry_times - 1:
                    return None
                await self._handle_rate_limit(attempt)
            except httpx.RequestError:
                return None
        
        return None
    
    async def _handle_rate_limit(self, attempt: int) -> None:
        """Handle rate limiting with exponential backoff"""
        import asyncio
        wait_time = (attempt + 1) * 10
        await asyncio.sleep(wait_time)
    
    @abstractmethod
    async def fetch(self, hours: int = 24) -> List[RawContent]:
        """Fetch content from source"""
        pass
    
    async def close(self) -> None:
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None
    
    def _is_within_time_window(
        self,
        published_at: Optional[datetime],
        hours: int
    ) -> bool:
        """Check if content is within time window"""
        if published_at is None:
            return True
        
        now = datetime.now(published_at.tzinfo) if published_at.tzinfo else datetime.now()
        delta = now - published_at
        return delta.total_seconds() <= hours * 3600
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication"""
        url = url.strip().lower()
        url = url.split("?")[0]
        url = url.split("#")[0]
        if url.endswith("/"):
            url = url[:-1]
        return url


class CrawlerFactory:
    """Factory for creating crawlers"""
    
    _crawlers = {}
    
    @classmethod
    def register(cls, source_type: SourceType, crawler_class: type):
        """Register a crawler class for a source type"""
        cls._crawlers[source_type] = crawler_class
    
    @classmethod
    def create(cls, source: Source) -> Optional[BaseCrawler]:
        """Create a crawler for the given source"""
        source_type = source.type if isinstance(source.type, SourceType) else SourceType(source.type)
        crawler_class = cls._crawlers.get(source_type)
        if crawler_class:
            return crawler_class(source)
        return None
    
    @classmethod
    def get_supported_types(cls) -> List[SourceType]:
        """Get list of supported source types"""
        return list(cls._crawlers.keys())


def register_crawler(source_type: SourceType):
    """Decorator to register a crawler class"""
    def decorator(crawler_class: type):
        CrawlerFactory.register(source_type, crawler_class)
        return crawler_class
    return decorator
