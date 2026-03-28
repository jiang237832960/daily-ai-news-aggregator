"""Parser for raw content"""

import re
from typing import Optional

from .models import RawContent, Article


class Parser:
    """Parse raw content into Article objects"""
    
    def __init__(self):
        self._content_length_limit = 5000
        self._summary_length = 500
    
    def parse(self, raw: RawContent, source_name: str, source_type: str) -> Article:
        """Parse RawContent into Article"""
        content = self._clean_html(raw.content) if raw.content else ""
        
        if not content and raw.title:
            summary = self._generate_summary_from_title(raw.title)
        else:
            summary = self._generate_summary(content)
        
        display_content = content if content else raw.title
        
        return Article(
            title=raw.title,
            title_raw=raw.title,
            url=raw.url,
            url_normalized=self._normalize_url(raw.url),
            summary=summary,
            content=display_content[:self._content_length_limit] if display_content else "",
            content_raw=raw.content,
            source=source_type,
            source_name=source_name,
            author=raw.author,
            published_at=raw.published_at,
            fetched_at=raw.fetched_at,
            engagement=raw.engagement,
            tags=self._extract_tags(raw.title, display_content)
        )
    
    def _generate_summary_from_title(self, title: str) -> str:
        """Generate summary from title when no content is available"""
        if not title:
            return ""
        return title
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from content"""
        if not text:
            return ""
        
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'&quot;', '"', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _generate_summary(self, content: str) -> str:
        """Generate summary from content"""
        if not content:
            return ""
        
        if len(content) <= self._summary_length:
            return content
        
        sentences = re.split(r'[.。!！?？]', content)
        summary = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if len(summary) + len(sentence) + 1 <= self._summary_length:
                summary += sentence + ". "
            else:
                break
        
        return summary.strip()
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication"""
        if not url:
            return ""
        
        url = url.strip().lower()
        url = url.split("?")[0]
        url = url.split("#")[0]
        url = url.rstrip("/")
        
        if url.startswith("https://news.ycombinator.com/item?id="):
            return url
        
        return url
    
    def _extract_tags(self, title: str, content: str) -> list[str]:
        """Extract tags from title and content"""
        tags = []
        
        tech_keywords = {
            "LLM", "GPT", "BERT", "Transformer", "Neural", "AI", "ML",
            "Computer Vision", "NLP", "Deep Learning", "Machine Learning",
            "OpenAI", "Anthropic", "Google", "Meta", "Microsoft",
            "PyTorch", "TensorFlow", "Keras", "LangChain", "RAG",
            "Agent", "RAG", "Embedding", "Vector", "Diffusion", "GAN"
        }
        
        text = (title + " " + content).upper()
        
        for keyword in tech_keywords:
            if keyword.upper() in text:
                tags.append(keyword)
        
        return list(set(tags))[:5]
    
    def is_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters"""
        if not text:
            return False
        return bool(re.search(r'[\u4e00-\u9fff]', text))
