"""Crawlers package"""

from .base import BaseCrawler
from .hackernews import HackerNewsCrawler
from .rss import RSSCrawler
from .reddit import RedditCrawler
from .arxiv import ArxivCrawler
from .github import GitHubCrawler
from .lobsters import LobstersCrawler
from .youtube import YouTubeCrawler

__all__ = [
    "BaseCrawler",
    "HackerNewsCrawler",
    "RSSCrawler",
    "RedditCrawler",
    "ArxivCrawler",
    "GitHubCrawler",
    "LobstersCrawler",
    "YouTubeCrawler"
]
