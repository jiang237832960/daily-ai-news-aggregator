"""Tests for parser module"""

import pytest
from datetime import datetime

from horizon.parser import Parser
from horizon.models import RawContent, Engagement


class TestParser:
    """Test cases for Parser"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = Parser()

    def test_clean_html(self):
        """Test HTML cleaning"""
        html = "<p>Hello <b>World</b>!</p><script>alert('xss')</script>"
        result = self.parser._clean_html(html)
        assert "Hello" in result
        assert "World" in result
        assert "<" not in result
        assert "alert" not in result

    def test_clean_html_special_chars(self):
        """Test HTML entity decoding"""
        html = "&nbsp;&amp;&lt;&gt;&quot;"
        result = self.parser._clean_html(html)
        assert " " in result
        assert "&" in result
        assert "<" in result
        assert ">" in result
        assert '"' in result

    def test_generate_summary_short_content(self):
        """Test summary generation with short content"""
        content = "Short content."
        result = self.parser._generate_summary(content)
        assert result == "Short content."

    def test_generate_summary_long_content(self):
        """Test summary generation with long content"""
        content = "This is sentence one. This is sentence two. This is sentence three. This is sentence four. This is sentence five."
        result = self.parser._generate_summary(content)
        assert len(result) <= 510
        assert result.endswith(".")

    def test_normalize_url(self):
        """Test URL normalization"""
        urls = [
            ("https://example.com/page", "https://example.com/page"),
            ("https://example.com/page?foo=bar", "https://example.com/page"),
            ("https://example.com/page#section", "https://example.com/page"),
            ("https://example.com/page/", "https://example.com/page"),
        ]
        for url, expected in urls:
            assert self.parser._normalize_url(url) == expected

    def test_normalize_url_hackernews(self):
        """Test HackerNews URL normalization preserves format"""
        url = "https://news.ycombinator.com/item?id=123456"
        result = self.parser._normalize_url(url)
        assert result == url

    def test_extract_tags_with_tech_keywords(self):
        """Test tag extraction with technical keywords"""
        title = "OpenAI releases GPT-5 with improved NLP capabilities"
        content = "The new model uses Transformer architecture and Deep Learning"
        tags = self.parser._extract_tags(title, content)
        
        assert "GPT" in tags or "AI" in tags or "NLP" in tags or "Transformer" in tags or "Deep Learning" in tags

    def test_extract_tags_limit(self):
        """Test tag extraction respects limit"""
        title = "A" * 100
        content = "B" * 100
        tags = self.parser._extract_tags(title, content)
        assert len(tags) <= 5

    def test_is_chinese(self):
        """Test Chinese character detection"""
        assert self.parser.is_chinese("你好世界")
        assert self.parser.is_chinese("Hello 世界")
        assert not self.parser.is_chinese("Hello World")
        assert not self.parser.is_chinese("")
        assert not self.parser.is_chinese(None)

    def test_parse_raw_content(self):
        """Test parsing RawContent to Article"""
        raw = RawContent(
            url="https://example.com/article",
            title="Test Article Title",
            content="<p>This is the article content with some <b>HTML</b>.</p>",
            author="Test Author",
            published_at=datetime(2026, 3, 28, 10, 0, 0),
            engagement=Engagement(comments=10, likes=100, shares=5)
        )
        
        article = self.parser.parse(raw, "TestSource", "rss")
        
        assert article.title == "Test Article Title"
        assert article.url == "https://example.com/article"
        assert article.author == "Test Author"
        assert article.source == "rss"
        assert article.source_name == "TestSource"
        assert article.engagement.comments == 10
        assert "<p>" not in article.content
        assert "<b>" not in article.content
