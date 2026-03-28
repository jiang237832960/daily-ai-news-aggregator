"""Tests for scorer module"""

import pytest
from datetime import datetime, timedelta

from horizon.scorer import RuleScorer
from horizon.models import Article, Config


class TestRuleScorer:
    """Test cases for RuleScorer"""

    def setup_method(self):
        """Setup test fixtures"""
        config = Config()
        self.scorer = RuleScorer(config)

    def test_keyword_bonus_breaking(self):
        """Test keyword bonus for breaking news"""
        score = self.scorer._calculate_keyword_bonus("Breaking: AI breakthrough announced")
        assert score >= 2

    def test_keyword_bonus_chinese(self):
        """Test keyword bonus for Chinese keywords"""
        score = self.scorer._calculate_keyword_bonus("突发：重大AI新闻")
        assert score >= 2

    def test_keyword_bonus_none(self):
        """Test no bonus for ordinary title"""
        score = self.scorer._calculate_keyword_bonus("Regular article title")
        assert score == 0

    def test_length_bonus_valid_range(self):
        """Test length bonus within valid range"""
        content = "A" * 5000
        score = self.scorer._calculate_length_bonus(content)
        assert score == 1

    def test_length_bonus_too_short(self):
        """Test no bonus for content too short"""
        content = "Short"
        score = self.scorer._calculate_length_bonus(content)
        assert score == 0

    def test_length_bonus_too_long(self):
        """Test no bonus for content too long"""
        content = "A" * 20000
        score = self.scorer._calculate_length_bonus(content)
        assert score == 0

    def test_length_bonus_empty(self):
        """Test no bonus for empty content"""
        score = self.scorer._calculate_length_bonus("")
        assert score == 0

    def test_freshness_bonus_recent(self):
        """Test freshness bonus for recent content"""
        published_at = datetime.now() - timedelta(hours=12)
        score = self.scorer._calculate_freshness_bonus(published_at)
        assert score == self.scorer.freshness_bonus

    def test_freshness_bonus_old(self):
        """Test no freshness bonus for old content"""
        published_at = datetime.now() - timedelta(hours=48)
        score = self.scorer._calculate_freshness_bonus(published_at)
        assert score == 0

    def test_freshness_bonus_none(self):
        """Test no freshness bonus when no date"""
        score = self.scorer._calculate_freshness_bonus(None)
        assert score == 0

    def test_technical_bonus_with_code(self):
        """Test technical bonus for content with code"""
        article = Article(
            title="API Integration Guide",
            content="Here is the code: def hello(): print('world')"
        )
        score = self.scorer._calculate_technical_bonus(article)
        assert score > 0

    def test_technical_bonus_with_github(self):
        """Test technical bonus for content with GitHub reference"""
        article = Article(
            title="Project Update",
            content="Check out https://github.com/user/repo for details"
        )
        score = self.scorer._calculate_technical_bonus(article)
        assert score > 0

    def test_calculate_max_score(self):
        """Test that score is capped at 10"""
        article = Article(
            title="突发 重磅 首发 Breaking Exclusive AI",
            content="A" * 5000 + " def code(): print('test') https://github.com",
            published_at=datetime.now() - timedelta(hours=1)
        )
        score = self.scorer.calculate(article)
        assert score <= 10.0

    def test_calculate_basic(self):
        """Test basic score calculation"""
        article = Article(
            title="Regular Article",
            content="A" * 5000,
            published_at=datetime.now() - timedelta(hours=25)
        )
        score = self.scorer.calculate(article)
        assert 0 <= score <= 10

    def test_cross_platform_bonus(self):
        """Test cross-platform convergence bonus"""
        article = Article(title="Test")
        
        bonus_single = self.scorer.calculate_cross_platform_bonus(article, 1)
        assert bonus_single == 0
        
        bonus_multiple = self.scorer.calculate_cross_platform_bonus(article, 3)
        assert bonus_multiple == 2
