"""Content fetcher with Scrapling integration"""

import asyncio
import re
import httpx
from typing import Optional
from urllib.parse import urlparse

from .models import RawContent, Engagement


class ContentFetcher:
    """Fetch content from URLs using httpx and Scrapling"""
    
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
    
    async def fetch(self, url: str) -> tuple[str, str]:
        """Fetch content from URL, returns (content, error)"""
        content = ""
        error_msg = ""
        
        try:
            client = await self._get_client()
            
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if self._is_protected_site(domain):
                content = await self._fetch_with_browser(client, url)
            else:
                content = await self._fetch_with_http(client, url)
                
            if not content:
                content = await self._fetch_with_http(client, url)
                
        except ImportError as e:
            error_msg = f"Import error: {e}"
        except Exception as e:
            error_msg = str(e)
        
        return content[:8000], error_msg
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
        return self._client
    
    async def _fetch_with_http(self, client: httpx.AsyncClient, url: str) -> str:
        """Fetch using simple HTTP request"""
        try:
            response = await client.get(url)
            if response.status_code == 200:
                if 'github.com' in url:
                    return await self._fetch_github_readme(client, url)
                return self._extract_content_from_html(response.text)
        except Exception:
            pass
        return ""
    
    async def _fetch_github_readme(self, client: httpx.AsyncClient, repo_url: str) -> str:
        """Fetch GitHub README directly"""
        import re
        match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
        if not match:
            return ""
        
        user, repo = match.groups()
        repo = repo.rstrip('/')
        
        for branch in ['main', 'master']:
            for filename in ['README.md', 'readme.md', 'README.MD']:
                readme_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{filename}"
                try:
                    response = await client.get(readme_url)
                    if response.status_code == 200:
                        return self._clean_readme(response.text)
                except Exception:
                    continue
        
        return ""
    
    async def _fetch_with_browser(self, client: httpx.AsyncClient, url: str) -> str:
        """Fetch using Scrapling browser (for protected sites)"""
        try:
            from scrapling.fetchers import AsyncFetcher
            
            async with AsyncFetcher() as fetcher:
                page = await fetcher.fetch(url)
                return self._extract_content_from_page(page)
        except Exception:
            pass
        return ""
    
    def _is_protected_site(self, domain: str) -> bool:
        """Check if domain needs browser fetching"""
        protected = [
            'github.com',
            'medium.com',
            'twitter.com',
            'x.com',
            'facebook.com',
            'linkedin.com',
        ]
        return any(d in domain for d in protected)
    
    def _extract_content_from_page(self, page) -> str:
        """Extract content from Scrapling page object"""
        try:
            for selector in [
                'article::text',
                'main::text', 
                '.post-content::text',
                '.article-content::text',
                '.entry-content::text',
                '#content::text',
            ]:
                try:
                    parts = page.css(selector).getall()
                    if parts:
                        text = ' '.join(t.strip() for t in parts if t.strip())
                        if len(text) > 100:
                            return self._clean_text(text)
                except Exception:
                    continue
        except Exception:
            pass
        return ""
    
    def _extract_content_from_html(self, html: str) -> str:
        """Extract main content from HTML"""
        if not html:
            return ""
        
        content = html
        
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        og_match = re.search(
            r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
            content, re.I
        )
        if og_match:
            return og_match.group(1)
        
        meta_match = re.search(
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
            content, re.I
        )
        if meta_match:
            return meta_match.group(1)
        
        article_match = re.search(
            r'<article[^>]*>(.*?)</article>',
            content, re.DOTALL | re.IGNORECASE
        )
        if article_match:
            content = article_match.group(1)
        
        main_match = re.search(
            r'<main[^>]*>(.*?)</main>',
            content, re.DOTALL | re.IGNORECASE
        )
        if main_match:
            content = main_match.group(1)
        
        content = re.sub(r'<[^>]+>', ' ', content)
        content = re.sub(r'\s+', ' ', content)
        
        return self._clean_text(content.strip())
    
    def _clean_readme(self, text: str) -> str:
        """Clean README markdown content"""
        if not text:
            return ""
        import re
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'[#*`>_~\[\]]', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()[:8000]
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        
        text = re.sub(r'[\[\]\(\)]+', ' ', text)
        text = re.sub(r'\.{3,}', '...', text)
        text = re.sub(r'\s+', ' ', text)
        
        sentences = re.split(r'[.。!！?？\n]', text)
        cleaned = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        return ' '.join(cleaned)[:8000]
    
    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
