"""Aggregator - main orchestrator for fetching and processing articles"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Tuple

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import ConfigLoader
from .database import Database
from .models import Article, Config, RawContent, Source
from .parser import Parser
from .translator import Translator
from .scorer import RuleScorer
from .ranker import HotnessRanker
from .deduplicator import Deduplicator
from .crawlers import (
    BaseCrawler,
    CrawlerFactory,
    HackerNewsCrawler,
    RSSCrawler,
    RedditCrawler,
    ArxivCrawler,
    GitHubCrawler,
    LobstersCrawler,
    YouTubeCrawler
)

console = Console()
logger = logging.getLogger(__name__)


class Aggregator:
    """Main aggregator for fetching and processing articles"""
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        db_path: Optional[str] = None
    ):
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load()
        self.db = Database(db_path)
        self.parser = Parser()
        self.translator = Translator(self.config)
        self.scorer = RuleScorer(self.config)
        self.ranker = HotnessRanker(self.config)
        self.deduplicator = Deduplicator()
    
    async def fetch_all(
        self,
        hours: int = 24,
        source_names: Optional[List[str]] = None,
        no_translate: bool = False
    ) -> Tuple[List[Article], dict]:
        """Fetch articles from all enabled sources"""
        enabled_sources = self.config_loader.get_enabled_sources()
        
        if source_names:
            enabled_sources = [
                s for s in enabled_sources
                if s.name.lower() in [n.lower() for n in source_names]
            ]
        
        all_articles: List[Article] = []
        stats = {
            "total_fetched": 0,
            "total_after_dedup": 0,
            "sources_processed": 0,
            "sources_failed": 0,
            "dedup_report": {}
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"[cyan]Fetching from {len(enabled_sources)} sources...",
                total=None
            )
            
            for source in enabled_sources:
                try:
                    articles = await self._fetch_source(source, hours)
                    all_articles.extend(articles)
                    stats["sources_processed"] += 1
                    stats["total_fetched"] += len(articles)
                    
                    console.print(f"[green]✓[/green] {source.name}: {len(articles)} articles")
                    
                except Exception as e:
                    logger.error(f"Failed to fetch from {source.name}: {e}")
                    stats["sources_failed"] += 1
                    console.print(f"[red]✗[/red] {source.name}: {str(e)}")
            
            progress.update(task, completed=True)
        
        if no_translate:
            self.translator.enabled = False
        
        console.print("\n[cyan]Processing articles...[/cyan]")
        processed_articles = await self._process_articles(all_articles)
        
        deduped_articles, dedup_report = self.deduplicator.deduplicate(processed_articles)
        stats["total_after_dedup"] = len(deduped_articles)
        stats["dedup_report"] = dedup_report
        
        for article in deduped_articles:
            self.db.save_article(article)
        
        return deduped_articles, stats
    
    async def _fetch_source(self, source: Source, hours: int) -> List[Article]:
        """Fetch articles from a single source"""
        crawler = CrawlerFactory.create(source)
        if not crawler:
            return []
        
        try:
            raw_contents = await crawler.fetch(hours)
            articles = []
            
            for raw in raw_contents:
                article = self.parser.parse(raw, source.name, source.type.value)
                articles.append(article)
            
            return articles
            
        finally:
            await crawler.close()
    
    async def _process_articles(self, articles: List[Article]) -> List[Article]:
        """Process articles: translate, score, rank"""
        processed = []
        
        for article in articles:
            article = await self.translator.translate_article(article)
            
            article.score = self.scorer.calculate(article)
            
            article.hotness = self.ranker.calculate(article)
            
            processed.append(article)
        
        return processed
    
    def get_articles(
        self,
        page: int = 1,
        limit: int = 50,
        source: Optional[str] = None,
        tag: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort: str = "hotness"
    ) -> List[Article]:
        """Get articles from database with filters"""
        return self.db.get_articles(
            page=page,
            limit=limit,
            source=source,
            tag=tag,
            date_from=date_from,
            date_to=date_to,
            sort=sort
        )
    
    def get_article_by_id(self, article_id: str) -> Optional[Article]:
        """Get article by ID"""
        return self.db.get_article_by_id(article_id)
    
    def mark_article_read(self, article_id: str) -> bool:
        """Mark article as read"""
        return self.db.mark_article_read(article_id)
