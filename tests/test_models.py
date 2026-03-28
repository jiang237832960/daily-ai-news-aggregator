"""Tests for models module"""

import pytest
from datetime import datetime

from horizon.models import (
    Article,
    Source,
    SourceType,
    Engagement,
    Summary,
    RawContent,
    Config
)


class TestArticle:
    """Test cases for Article model"""

    def test_create_article(self):
        """Test article creation"""
        article = Article(
            title="Test Article",
            url="https://example.com",
            source="rss",
            source_name="Test RSS"
        )
        assert article.title == "Test Article"
        assert article.url == "https://example.com"
        assert article.id is not None

    def test_article_defaults(self):
        """Test article default values"""
        article = Article()
        assert article.score == 0.0
        assert article.hotness == 0.0
        assert article.is_read is False
        assert article.is_archived is False
        assert article.tags == []

    def test_article_engagement(self):
        """Test article with engagement"""
        article = Article(
            title="Popular Article",
            engagement=Engagement(comments=10, likes=100, shares=5)
        )
        assert article.engagement.comments == 10
        assert article.engagement.likes == 100
        assert article.engagement.shares == 5


class TestSource:
    """Test cases for Source model"""

    def test_create_source(self):
        """Test source creation"""
        source = Source(
            name="HackerNews",
            type=SourceType.HACKERNEWS
        )
        assert source.name == "HackerNews"
        assert source.type == SourceType.HACKERNEWS
        assert source.enabled is True
        assert source.weight == 5.0

    def test_source_defaults(self):
        """Test source default values"""
        source = Source(name="Test", type=SourceType.RSS)
        assert source.enabled is True
        assert source.weight == 5.0
        assert source.timeout == 30
        assert source.retry_times == 3
        assert source.failure_count == 0


class TestSourceType:
    """Test cases for SourceType enum"""

    def test_source_types(self):
        """Test source type values"""
        assert SourceType.HACKERNEWS.value == "hackernews"
        assert SourceType.RSS.value == "rss"
        assert SourceType.REDDIT.value == "reddit"
        assert SourceType.GITHUB.value == "github"
        assert SourceType.ARXIV.value == "arxiv"


class TestEngagement:
    """Test cases for Engagement model"""

    def test_create_engagement(self):
        """Test engagement creation"""
        e = Engagement(comments=5, likes=50, shares=10)
        assert e.comments == 5
        assert e.likes == 50
        assert e.shares == 10

    def test_engagement_defaults(self):
        """Test engagement default values"""
        e = Engagement()
        assert e.comments == 0
        assert e.likes == 0
        assert e.shares == 0


class TestSummary:
    """Test cases for Summary model"""

    def test_create_summary(self):
        """Test summary creation"""
        summary = Summary(
            date="2026-03-28",
            content="# Daily Digest",
            article_count=10
        )
        assert summary.date == "2026-03-28"
        assert summary.article_count == 10


class TestRawContent:
    """Test cases for RawContent model"""

    def test_create_raw_content(self):
        """Test raw content creation"""
        raw = RawContent(
            url="https://example.com",
            title="Test",
            content="Content here"
        )
        assert raw.url == "https://example.com"
        assert raw.title == "Test"

    def test_raw_content_engagement(self):
        """Test raw content with engagement"""
        raw = RawContent(
            url="https://example.com",
            title="Test",
            engagement=Engagement(comments=1, likes=2, shares=3)
        )
        assert raw.engagement.comments == 1


class TestConfig:
    """Test cases for Config model"""

    def test_create_config(self):
        """Test config creation"""
        config = Config()
        assert config.version == 1
        assert config.translation is not None
        assert config.scoring is not None

    def test_config_sources(self):
        """Test config with sources"""
        source = Source(name="Test", type=SourceType.RSS)
        config = Config(sources=[source])
        assert len(config.sources) == 1
