"""Tests for deduplicator module"""

import pytest
from datetime import datetime

from horizon.deduplicator import Deduplicator
from horizon.models import Article, Engagement


class TestDeduplicator:
    """Test cases for Deduplicator"""

    def setup_method(self):
        """Setup test fixtures"""
        self.dedup = Deduplicator()

    def test_deduplicate_empty_list(self):
        """Test deduplication of empty list"""
        articles, report = self.dedup.deduplicate([])
        assert len(articles) == 0
        assert report["total_input"] == 0

    def test_deduplicate_unique_articles(self):
        """Test deduplication with unique articles"""
        articles = [
            Article(id="1", title="Article 1", url="https://example.com/1"),
            Article(id="2", title="Article 2", url="https://example.com/2"),
        ]
        result, report = self.dedup.deduplicate(articles)
        assert len(result) == 2
        assert report["total_duplicates"] == 0

    def test_deduplicate_same_url(self):
        """Test deduplication by URL"""
        articles = [
            Article(id="1", title="Article 1", url="https://example.com/same"),
            Article(id="2", title="Article 2", url="https://example.com/same"),
        ]
        result, report = self.dedup.deduplicate(articles)
        assert len(result) == 1
        assert report["url_duplicates"] == 1

    def test_deduplicate_normalized_url(self):
        """Test deduplication with normalized URLs"""
        articles = [
            Article(id="1", title="Article 1", url="https://example.com/page/"),
            Article(id="2", title="Article 2", url="https://example.com/page"),
        ]
        result, report = self.dedup.deduplicate(articles)
        assert len(result) == 1
        assert report["url_duplicates"] == 1

    def test_normalize_url_with_query_params(self):
        """Test URL normalization removes query params"""
        url = "https://example.com/page?utm_source=test"
        result = self.dedup._normalize_url(url)
        assert "?" not in result

    def test_normalize_url_with_fragment(self):
        """Test URL normalization removes fragment"""
        url = "https://example.com/page#section"
        result = self.dedup._normalize_url(url)
        assert "#" not in result

    def test_normalize_url_trailing_slash(self):
        """Test URL normalization removes trailing slash"""
        url = "https://example.com/page/"
        result = self.dedup._normalize_url(url)
        assert result == "https://example.com/page"

    def test_calculate_title_similarity_identical(self):
        """Test similarity for identical titles"""
        similarity = self.dedup._calculate_title_similarity(
            "Same Title",
            "Same Title"
        )
        assert similarity == 1.0

    def test_calculate_title_similarity_different(self):
        """Test similarity for different titles"""
        similarity = self.dedup._calculate_title_similarity(
            "Article About AI",
            "Article About ML"
        )
        assert 0 < similarity < 1

    def test_calculate_title_similarity_case_insensitive(self):
        """Test similarity is case insensitive"""
        s1 = self.dedup._calculate_title_similarity("Title", "title")
        s2 = self.dedup._calculate_title_similarity("TITLE", "title")
        assert abs(s1 - s2) < 0.01

    def test_levenshtein_distance_identical(self):
        """Test distance for identical strings"""
        distance = self.dedup._levenshtein_distance("same", "same")
        assert distance == 0

    def test_levenshtein_distance_one_char_diff(self):
        """Test distance for one character difference"""
        distance = self.dedup._levenshtein_distance("cat", "bat")
        assert distance == 1

    def test_levenshtein_distance_empty(self):
        """Test distance with empty string"""
        distance = self.dedup._levenshtein_distance("abc", "")
        assert distance == 3
