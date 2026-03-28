"""HackerNews crawler with content fetching"""

import re
from datetime import datetime
from typing import List, Optional

from ..models import SourceType, RawContent
from .base import BaseCrawler, register_crawler


@register_crawler(SourceType.HACKERNEWS)
class HackerNewsCrawler(BaseCrawler):
    """Crawler for HackerNews with content fetching"""
    
    HN_API_URL = "https://hacker-news.firebaseio.com/v0"
    GITHUB_RAW_URL = "https://raw.githubusercontent.com"
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.HACKERNEWS
    
    async def fetch(self, hours: int = 24) -> List[RawContent]:
        """Fetch top stories from HackerNews with content"""
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
                
                external_url = story.get("url", "")
                content = ""
                
                if external_url:
                    content = await self._fetch_content(external_url)
                
                if not content and story.get("text"):
                    content = self._clean_html(story["text"])
                
                article = RawContent(
                    url=external_url or f"https://news.ycombinator.com/item?id={story_id}",
                    title=story.get("title", ""),
                    content=content,
                    author=story.get("by", ""),
                    published_at=published_at,
                    engagement=self._extract_engagement(story)
                )
                articles.append(article)
                
            except Exception as e:
                continue
        
        return articles
    
    async def _fetch_content(self, url: str) -> str:
        """Fetch content from external URL"""
        try:
            if "github.com" in url:
                readme_url = await self._find_github_readme(url)
                if readme_url:
                    response = await self._fetch_with_retry(readme_url, timeout=5)
                    if response and response.status_code == 200:
                        return self._clean_markdown(response.text[:8000])
            
            response = await self._fetch_with_retry(url, timeout=5)
            if response and response.status_code == 200:
                return self._extract_main_content(response.text[:15000])
                
        except Exception:
            pass
        return ""
    
    def _convert_github_to_raw(self, url: str) -> Optional[str]:
        """Convert GitHub blob URL to raw URL"""
        match = re.search(r"github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)", url)
        if match:
            user, repo, _, path = match.groups()
            return f"https://raw.githubusercontent.com/{user}/{repo}/{path}"
        return None
    
    async def _find_github_readme(self, repo_url: str) -> Optional[str]:
        """Find README URL for a GitHub repository"""
        match = re.search(r"github\.com/([^/]+)/([^/]+)/?", repo_url)
        if not match:
            return None
        
        user, repo = match.groups()
        repo = repo.rstrip("/")
        
        for branch in ["main", "master"]:
            for filename in ["README.md", "readme.md", "Readme.md"]:
                readme_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{filename}"
                response = await self._fetch_with_retry(readme_url)
                if response and response.status_code == 200:
                    return readme_url
        return None
    
    def _extract_main_content(self, html: str) -> str:
        """Extract main content from HTML"""
        content = html
        
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        
        meta_desc = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', content, re.I)
        if meta_desc:
            return meta_desc.group(1)
        
        og_desc = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']', content, re.I)
        if og_desc:
            return og_desc.group(1)
        
        article_match = re.search(r'<article[^>]*>(.*?)</article>', content, re.DOTALL | re.I)
        if article_match:
            content = article_match.group(1)
        
        main_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL | re.I)
        if main_match:
            content = main_match.group(1)
        
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()[:5000]
    
    def _clean_markdown(self, text: str) -> str:
        """Clean markdown text"""
        if not text:
            return ""
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'[#*`>_~\[\]]', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()[:5000]
    
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
