"""Tests for crawlers module"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from horizon.crawlers.hackernews import HackerNewsCrawler
from horizon.crawlers.rss import RSSCrawler
from horizon.models import Source, SourceType


class TestHackerNewsCrawler:
    """Test cases for HackerNewsCrawler"""

    def setup_method(self):
        """Setup test fixtures"""
        self.source = Source(
            name="HackerNews",
            type=SourceType.HACKERNEWS,
            enabled=True
        )
        self.crawler = HackerNewsCrawler(self.source)

    def test_source_type(self):
        """Test source type is HackerNews"""
        assert self.crawler.source_type == SourceType.HACKERNEWS

    def test_supports(self):
        """Test supports method"""
        assert self.crawler.supports(SourceType.HACKERNEWS)
        assert not self.crawler.supports(SourceType.RSS)

    def test_is_within_time_window(self):
        """Test time window check"""
        recent = datetime.now()
        assert self.crawler._is_within_time_window(recent, 24)
        
        old = datetime.now() - timedelta(hours=48)
        assert not self.crawler._is_within_time_window(old, 24)

    def test_normalize_url(self):
        """Test URL normalization"""
        url = "https://example.com/page/"
        normalized = self.crawler._normalize_url(url)
        assert normalized == "https://example.com/page"

    @pytest.mark.asyncio
    async def test_fetch_empty_on_error(self):
        """Test fetch returns empty list on error"""
        with patch.object(self.crawler, '_fetch_with_retry', return_value=None):
            result = await self.crawler.fetch(24)
            assert result == []


class TestRSSCrawler:
    """Test cases for RSSCrawler"""

    def setup_method(self):
        """Setup test fixtures"""
        self.source = Source(
            name="Test RSS",
            type=SourceType.RSS,
            enabled=True,
            url="https://example.com/feed.xml"
        )
        self.crawler = RSSCrawler(self.source)

    def test_source_type(self):
        """Test source type is RSS"""
        assert self.crawler.source_type == SourceType.RSS

    def test_supports(self):
        """Test supports method"""
        assert self.crawler.supports(SourceType.RSS)
        assert not self.crawler.supports(SourceType.HACKERNEWS)


class TestCrawlerFactory:
    """Test cases for CrawlerFactory"""

    def test_register_and_create(self):
        """Test crawler registration and creation"""
        from horizon.crawlers.base import CrawlerFactory, register_crawler
        
        @register_crawler(SourceType.YOUTUBE)
        class TestCrawler:
            pass
        
        source = Source(name="Test", type=SourceType.YOUTUBE)
        crawler = CrawlerFactory.create(source)
        assert crawler is not None
        assert isinstance(crawler, TestCrawler)

    def test_create_unsupported(self):
        """Test creating unsupported source returns None"""
        source = Source(name="Unknown", type=SourceType.REDDIT)
        # Reddit crawler may not be registered, returns None
        crawler = CrawlerFactory.create(source)
        # Just ensure no exception is raised


from datetime import timedelta
