"""YouTube crawler"""

from datetime import datetime
from typing import List

from ..models import SourceType, RawContent
from .base import BaseCrawler, register_crawler


@register_crawler(SourceType.YOUTUBE)
class YouTubeCrawler(BaseCrawler):
    """Crawler for YouTube"""
    
    YOUTUBE_API = "https://www.googleapis.com/youtube/v3"
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.YOUTUBE
    
    async def fetch(self, hours: int = 24) -> List[RawContent]:
        """Fetch latest videos from YouTube channel"""
        articles = []
        
        channel_id = self.source.url or ""
        api_key = self.source.auth_config.get("api_key", "")
        
        if not channel_id or not api_key:
            return articles
        
        url = f"{self.YOUTUBE_API}/search"
        params = {
            "key": api_key,
            "channelId": channel_id,
            "part": "snippet",
            "order": "date",
            "maxResults": 20,
            "type": "video"
        }
        
        response = await self._fetch_with_retry(url, params=params)
        if not response:
            return articles
        
        try:
            data = response.json()
            items = data.get("items", [])
            
            for item in items:
                snippet = item.get("snippet", {})
                published_at_str = snippet.get("publishedAt", "")
                
                published_at = None
                if published_at_str:
                    published_at = datetime.fromisoformat(
                        published_at_str.replace("Z", "+00:00")
                    )
                
                if not self._is_within_time_window(published_at, hours):
                    continue
                
                video_id = item.get("id", {}).get("videoId", "")
                
                article = RawContent(
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    title=snippet.get("title", ""),
                    content=snippet.get("description", ""),
                    author=snippet.get("channelTitle", ""),
                    published_at=published_at
                )
                articles.append(article)
                
        except Exception:
            pass
        
        return articles
