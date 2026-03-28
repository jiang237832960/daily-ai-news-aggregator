"""Hotness ranker for articles"""

from datetime import datetime

from .models import Article, Config


class HotnessRanker:
    """Calculate article hotness score"""
    
    WEIGHTS = {
        "source_authority": 0.30,
        "rule_score": 0.30,
        "recency": 0.25,
        "engagement": 0.15
    }
    
    DECAY_RATE = 0.10
    DECAY_INTERVAL_HOURS = 24
    
    def __init__(self, config: Config):
        self.config = config
        self.source_weights = {
            src.name: src.weight for src in config.sources
        }
    
    def calculate(self, article: Article) -> float:
        """Calculate hotness score for article"""
        source_weight = self.source_weights.get(article.source_name, 5.0) / 10.0
        
        rule_score_normalized = article.score / 10.0
        
        recency_score = self._calculate_recency_score(article.published_at)
        
        engagement_score = self._calculate_engagement_score(article)
        
        hotness = (
            source_weight * self.WEIGHTS["source_authority"] +
            rule_score_normalized * self.WEIGHTS["rule_score"] +
            recency_score * self.WEIGHTS["recency"] +
            engagement_score * self.WEIGHTS["engagement"]
        ) * 100
        
        return round(hotness, 2)
    
    def _calculate_recency_score(self, published_at: datetime) -> float:
        """Calculate recency score with time decay"""
        if not published_at:
            return 0.5
        
        now = datetime.now(published_at.tzinfo) if published_at.tzinfo else datetime.now()
        hours_ago = (now - published_at).total_seconds() / 3600
        
        decay_factor = 1.0 - (hours_ago / self.DECAY_INTERVAL_HOURS) * self.DECAY_RATE
        decay_factor = max(decay_factor, 0.1)
        
        return decay_factor
    
    def _calculate_engagement_score(self, article: Article) -> float:
        """Calculate engagement score"""
        comments = article.engagement.comments
        likes = article.engagement.likes
        shares = article.engagement.shares
        
        total_engagement = comments + likes + shares * 2
        
        if total_engagement == 0:
            return 0.0
        
        import math
        return min(math.log10(total_engagement + 1) / 3, 1.0)
    
    def calculate_topic_hotness(self, articles: list[Article]) -> float:
        """Calculate combined hotness for topic (multiple articles)"""
        if not articles:
            return 0.0
        
        total_hotness = sum(a.hotness for a in articles)
        convergence_bonus = 1.0 + (len(articles) - 1) * 0.1
        
        return total_hotness * convergence_bonus
