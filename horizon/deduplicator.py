"""Deduplicator for articles"""

import hashlib
from typing import Dict, List, Tuple

from .models import Article


class Deduplicator:
    """Deduplicate articles based on URL and content similarity"""
    
    SIMILARITY_THRESHOLD = 0.85
    
    def __init__(self):
        self._seen_urls: Dict[str, Article] = {}
        self._seen_hashes: Dict[str, str] = {}
    
    def deduplicate(self, articles: List[Article]) -> Tuple[List[Article], Dict]:
        """Deduplicate articles and return unique ones with report"""
        unique_articles = []
        duplicates = []
        url_duplicates = 0
        similarity_duplicates = 0
        
        for article in articles:
            is_duplicate, dup_type = self._check_duplicate(article)
            
            if is_duplicate:
                duplicates.append({
                    "article": article,
                    "type": dup_type
                })
                if dup_type == "url":
                    url_duplicates += 1
                else:
                    similarity_duplicates += 1
            else:
                unique_articles.append(article)
                self._add_to_seen(article)
        
        report = {
            "total_input": len(articles),
            "unique_count": len(unique_articles),
            "url_duplicates": url_duplicates,
            "similarity_duplicates": similarity_duplicates,
            "total_duplicates": len(duplicates)
        }
        
        return unique_articles, report
    
    def _check_duplicate(self, article: Article) -> Tuple[bool, str]:
        """Check if article is a duplicate"""
        normalized_url = article.url_normalized or self._normalize_url(article.url)
        
        if normalized_url in self._seen_urls:
            return True, "url"
        
        md5_hash = self._calculate_md5(article)
        if md5_hash in self._seen_hashes:
            return True, "content"
        
        for seen_article in self._seen_urls.values():
            similarity = self._calculate_title_similarity(
                article.title,
                seen_article.title
            )
            if similarity >= self.SIMILARITY_THRESHOLD:
                return True, "similarity"
        
        return False, ""
    
    def _add_to_seen(self, article: Article) -> None:
        """Add article to seen tracking"""
        normalized_url = article.url_normalized or self._normalize_url(article.url)
        self._seen_urls[normalized_url] = article
        
        md5_hash = self._calculate_md5(article)
        self._seen_hashes[md5_hash] = normalized_url
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for comparison"""
        if not url:
            return ""
        
        url = url.strip().lower()
        url = url.split("?")[0]
        url = url.split("#")[0]
        url = url.rstrip("/")
        
        if url.startswith("https://news.ycombinator.com/item?id="):
            return url
        
        return url
    
    def _calculate_md5(self, article: Article) -> str:
        """Calculate MD5 hash of article content"""
        content = (article.title or "") + (article.content or "")
        return hashlib.md5(content.encode()).hexdigest()
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate title similarity using edit distance"""
        if not title1 or not title2:
            return 0.0
        
        title1 = title1.lower().strip()
        title2 = title2.lower().strip()
        
        if title1 == title2:
            return 1.0
        
        distance = self._levenshtein_distance(title1, title2)
        max_len = max(len(title1), len(title2))
        
        if max_len == 0:
            return 0.0
        
        similarity = 1.0 - (distance / max_len)
        return similarity
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein edit distance"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            
            previous_row = current_row
        
        return previous_row[-1]
