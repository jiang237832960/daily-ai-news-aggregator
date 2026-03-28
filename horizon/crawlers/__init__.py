"""Crawlers package"""

from .base import BaseCrawler, CrawlerFactory, register_crawler
from .hackernews import HackerNewsCrawler
from .rss import RSSCrawler
from .reddit import RedditCrawler
from .arxiv import ArxivCrawler
from .github import GitHubCrawler
from .lobsters import LobstersCrawler
from .youtube import YouTubeCrawler

__all__ = [
    "BaseCrawler",
    "CrawlerFactory",
    "register_crawler",
    "HackerNewsCrawler",
    "RSSCrawler",
    "RedditCrawler",
    "ArxivCrawler",
    "GitHubCrawler",
    "LobstersCrawler",
    "YouTubeCrawler"
]
