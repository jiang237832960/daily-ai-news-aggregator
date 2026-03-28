"""Rule-based scorer for article quality"""

import re
from datetime import datetime, timedelta
from typing import Dict

from .models import Article, Config


class RuleScorer:
    """Rule-based article quality scorer"""
    
    MAX_SCORE = 10.0
    
    def __init__(self, config: Config):
        self.config = config
        self.scoring_config = config.scoring
        self.keywords: Dict[str, float] = self.scoring_config.get("keywords", {
            "突发": 2, "重磅": 2, "首发": 2,
            "breaking": 2, "exclusive": 2
        })
        self.length_bonus = self.scoring_config.get("length_bonus", {
            "min": 1000, "max": 10000, "score": 1
        })
        self.freshness_hours = self.scoring_config.get("freshness_hours", 24)
        self.freshness_bonus = self.scoring_config.get("freshness_bonus", 2)
    
    def calculate(self, article: Article) -> float:
        """Calculate quality score for article (0-10)"""
        score = 0.0
        
        score += self._calculate_keyword_bonus(article.title)
        
        score += self._calculate_length_bonus(article.content)
        
        score += self._calculate_freshness_bonus(article.published_at)
        
        score += self._calculate_technical_bonus(article)
        
        return min(score, self.MAX_SCORE)
    
    def _calculate_keyword_bonus(self, title: str) -> float:
        """Calculate bonus from keywords in title"""
        if not title:
            return 0.0
        
        title_upper = title.upper()
        bonus = 0.0
        
        for keyword, weight in self.keywords.items():
            if keyword.upper() in title_upper:
                bonus += weight
        
        return bonus
    
    def _calculate_length_bonus(self, content: str) -> float:
        """Calculate bonus from content length"""
        if not content:
            return 0.0
        
        content_length = len(content)
        min_len = self.length_bonus.get("min", 1000)
        max_len = self.length_bonus.get("max", 10000)
        bonus_score = self.length_bonus.get("score", 1)
        
        if min_len <= content_length <= max_len:
            return bonus_score
        
        return 0.0
    
    def _calculate_freshness_bonus(self, published_at: datetime) -> float:
        """Calculate bonus for fresh content"""
        if not published_at:
            return 0.0
        
        now = datetime.now(published_at.tzinfo) if published_at.tzinfo else datetime.now()
        hours_ago = (now - published_at).total_seconds() / 3600
        
        if hours_ago <= self.freshness_hours:
            return self.freshness_bonus
        
        return 0.0
    
    def _calculate_technical_bonus(self, article: Article) -> float:
        """Calculate bonus for technical content"""
        if not article.content and not article.title:
            return 0.0
        
        text = (article.title + " " + article.content).upper()
        
        technical_indicators = [
            r'def\s+\w+\s*\(',
            r'class\s+\w+',
            r'import\s+\w+',
            r'from\s+\w+\s+import',
            r'api\s*[:=]',
            r'https?://',
            r'\w+\.\w+\.\w+',
            r'\d+\.\d+',
            r'github\.com',
            r'gitlab\.com',
            r'```',
        ]
        
        bonus = 0.0
        for indicator in technical_indicators:
            if re.search(indicator, text):
                bonus += 0.2
        
        return min(bonus, 1.0)
    
    def calculate_cross_platform_bonus(
        self,
        article: Article,
        same_topic_count: int
    ) -> float:
        """Calculate bonus for cross-platform convergence"""
        if same_topic_count > 1:
            return 2.0
        return 0.0
