"""Tests for ranker module"""

import pytest
from datetime import datetime, timedelta

from horizon.ranker import HotnessRanker
from horizon.models import Article, Engagement, Config, Source, SourceType


class TestHotnessRanker:
    """Test cases for HotnessRanker"""

    def setup_method(self):
        """Setup test fixtures"""
        config = Config(sources=[
            Source(name="HackerNews", type=SourceType.HACKERNEWS, weight=8.0),
            Source(name="Reddit", type=SourceType.REDDIT, weight=7.0),
        ])
        self.ranker = HotnessRanker(config)

    def test_calculate_basic(self):
        """Test basic hotness calculation"""
        article = Article(
            title="Test Article",
            url="https://example.com",
            score=7.0,
            published_at=datetime.now() - timedelta(hours=1),
            engagement=Engagement(comments=10, likes=100, shares=5)
        )
        hotness = self.ranker.calculate(article)
        assert hotness >= 0
        assert hotness <= 100

    def test_calculate_without_published_date(self):
        """Test calculation without published date"""
        article = Article(
            title="Test",
            url="https://example.com",
            score=5.0
        )
        hotness = self.ranker.calculate(article)
        assert hotness >= 0

    def test_time_decay_recent(self):
        """Test time decay for recent content"""
        score = self.ranker._calculate_recency_score(
            datetime.now() - timedelta(hours=1)
        )
        assert score >= 0.9

    def test_time_decay_old(self):
        """Test time decay for old content"""
        score = self.ranker._calculate_recency_score(
            datetime.now() - timedelta(hours=48)
        )
        assert score < 0.9

    def test_time_decay_minimum(self):
        """Test time decay minimum floor"""
        score = self.ranker._calculate_recency_score(
            datetime.now() - timedelta(days=30)
        )
        assert score >= 0.1

    def test_engagement_score_zero(self):
        """Test engagement score with no engagement"""
        article = Article(
            title="Test",
            url="https://example.com",
            engagement=Engagement(comments=0, likes=0, shares=0)
        )
        score = self.ranker._calculate_engagement_score(article)
        assert score == 0.0

    def test_engagement_score_high(self):
        """Test engagement score with high engagement"""
        article = Article(
            title="Test",
            url="https://example.com",
            engagement=Engagement(comments=1000, likes=5000, shares=500)
        )
        score = self.ranker._calculate_engagement_score(article)
        assert score > 0

    def test_engagement_score_capped(self):
        """Test engagement score is capped at 1.0"""
        article = Article(
            title="Test",
            url="https://example.com",
            engagement=Engagement(comments=100000, likes=1000000, shares=100000)
        )
        score = self.ranker._calculate_engagement_score(article)
        assert score <= 1.0

    def test_calculate_topic_hotness_single(self):
        """Test topic hotness with single article"""
        articles = [
            Article(title="Test 1", url="https://example.com/1", hotness=50.0)
        ]
        hotness = self.ranker.calculate_topic_hotness(articles)
        assert hotness == 50.0

    def test_calculate_topic_hotness_multiple(self):
        """Test topic hotness with multiple articles"""
        articles = [
            Article(title="Test 1", url="https://example.com/1", hotness=50.0),
            Article(title="Test 2", url="https://example.com/2", hotness=40.0),
        ]
        hotness = self.ranker.calculate_topic_hotness(articles)
        assert hotness > 90

    def test_calculate_topic_hotness_empty(self):
        """Test topic hotness with empty list"""
        hotness = self.ranker.calculate_topic_hotness([])
        assert hotness == 0.0

    def test_weights_sum_to_one(self):
        """Test that weights sum to 1.0"""
        total = sum(self.ranker.WEIGHTS.values())
        assert abs(total - 1.0) < 0.001
