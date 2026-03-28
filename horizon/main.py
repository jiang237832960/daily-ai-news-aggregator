"""Horizon CLI - Main entry point"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .aggregator import Aggregator
from .config import ConfigLoader

console = Console()
app = typer.Typer(help="Horizon - AI News Aggregator & Translator")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@app.command()
def fetch(
    hours: int = typer.Option(24, "--hours", "-h", help="Time window in hours"),
    sources: Optional[str] = typer.Option(None, "--sources", "-s", help="Comma-separated source names"),
    no_translate: bool = typer.Option(False, "--no-translate", help="Disable translation"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
) -> None:
    """Fetch news from all enabled sources"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    source_list = None
    if sources:
        source_list = [s.strip() for s in sources.split(",")]
    
    async def run():
        aggregator = Aggregator()
        console.print(f"[bold cyan]Fetching news from last {hours} hours...[/bold cyan]")
        
        articles, stats = await aggregator.fetch_all(
            hours=hours,
            source_names=source_list,
            no_translate=no_translate
        )
        
        console.print("\n[bold green]Fetch Complete![/bold green]")
        console.print(f"Total fetched: {stats['total_fetched']}")
        console.print(f"After deduplication: {stats['total_after_dedup']}")
        console.print(f"Sources processed: {stats['sources_processed']}")
        console.print(f"Sources failed: {stats['sources_failed']}")
        
        if stats.get("dedup_report"):
            report = stats["dedup_report"]
            console.print(f"\n[bold]Deduplication Report:[/bold]")
            console.print(f"  URL duplicates: {report.get('url_duplicates', 0)}")
            console.print(f"  Similarity duplicates: {report.get('similarity_duplicates', 0)}")
    
    asyncio.run(run())


@app.command()
def list_sources() -> None:
    """List all configured sources"""
    config_loader = ConfigLoader()
    config = config_loader.load()
    
    table = Table(title="Configured Sources")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Enabled", style="green")
    table.add_column("Weight", justify="right")
    
    for source in config.sources:
        status = "✓" if source.enabled else "✗"
        status_style = "green" if source.enabled else "red"
        table.add_row(
            source.name,
            source.type.value,
            f"[{status_style}]{status}[/{status_style}]",
            f"{source.weight:.1f}"
        )
    
    console.print(table)


@app.command()
def digest(
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of articles"),
    publish: bool = typer.Option(False, "--publish", help="Publish to GitHub Pages")
) -> None:
    """Generate daily digest"""
    target_date = datetime.now().strftime("%Y-%m-%d") if not date else date
    
    aggregator = Aggregator()
    articles = aggregator.get_articles(
        page=1,
        limit=limit,
        sort="hotness"
    )
    
    today_articles = [
        a for a in articles
        if a.published_at and a.published_at.strftime("%Y-%m-%d") == target_date
    ]
    
    if not today_articles:
        today_articles = articles[:limit]
    
    markdown = f"# AI资讯日报 - {target_date}\n\n"
    markdown += f"共 {len(today_articles)} 篇文章\n\n"
    markdown += "---\n\n"
    
    for i, article in enumerate(today_articles[:limit], 1):
        markdown += f"## {i}. {article.title}\n\n"
        markdown += f"来源: {article.source_name} | "
        if article.published_at:
            markdown += f"发布时间: {article.published_at.strftime('%Y-%m-%d %H:%M')}\n"
        markdown += f"\n{article.summary}\n\n"
        markdown += f"[阅读更多]({article.url})\n\n"
        markdown += "---\n\n"
    
    output_dir = Path("data/summaries")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{target_date}.md"
    output_file.write_text(markdown, encoding="utf-8")
    
    console.print(f"[green]Digest generated: {output_file}[/green]")


@app.command()
def stats(
    days: int = typer.Option(7, "--days", "-d", help="Number of days to analyze"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text/json")
) -> None:
    """Show statistics"""
    aggregator = Aggregator()
    
    date_from = datetime.now() - timedelta(days=days)
    articles = aggregator.get_articles(
        page=1,
        limit=1000,
        date_from=date_from,
        sort="hotness"
    )
    
    source_counts = {}
    total_engagement = {"comments": 0, "likes": 0, "shares": 0}
    
    for article in articles:
        source_counts[article.source_name] = source_counts.get(article.source_name, 0) + 1
        total_engagement["comments"] += article.engagement.comments
        total_engagement["likes"] += article.engagement.likes
        total_engagement["shares"] += article.engagement.shares
    
    if format == "json":
        import json
        data = {
            "period_days": days,
            "total_articles": len(articles),
            "source_distribution": source_counts,
            "total_engagement": total_engagement,
            "avg_score": sum(a.score for a in articles) / len(articles) if articles else 0
        }
        console.print(json.dumps(data, indent=2, default=str))
    else:
        table = Table(title=f"Statistics (Last {days} Days)")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="green")
        
        table.add_row("Total Articles", str(len(articles)))
        table.add_row("Avg Score", f"{sum(a.score for a in articles) / len(articles):.2f}" if articles else "N/A")
        table.add_row("Total Comments", str(total_engagement["comments"]))
        table.add_row("Total Likes", str(total_engagement["likes"]))
        
        console.print(table)
        
        if source_counts:
            console.print("\n[bold]Source Distribution:[/bold]")
            for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
                console.print(f"  {source}: {count}")


@app.command()
def wizard() -> None:
    """Interactive configuration wizard"""
    console.print("[bold cyan]Horizon Configuration Wizard[/bold cyan]\n")
    
    config_loader = ConfigLoader()
    config = config_loader.load()
    
    console.print("[yellow]This wizard will help you configure Horizon.[/yellow]")
    console.print("[yellow]For now, the default configuration has been created.[/yellow]")
    console.print(f"\n[green]Config file: {config_loader.config_path}[/green]")


if __name__ == "__main__":
    app()
