"""FastAPI application for Horizon"""

from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .aggregator import Aggregator
from .models import Article

app = FastAPI(
    title="Horizon API",
    description="AI News Aggregator & Translator API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

aggregator: Optional[Aggregator] = None


def get_aggregator() -> Aggregator:
    global aggregator
    if aggregator is None:
        aggregator = Aggregator()
    return aggregator


class ArticleResponse(BaseModel):
    id: str
    title: str
    title_raw: Optional[str] = None
    url: str
    summary: str
    content: Optional[str] = None
    source: str
    source_name: str
    author: str
    published_at: Optional[datetime] = None
    fetched_at: datetime
    score: float
    hotness: float
    engagement_comments: int = 0
    engagement_likes: int = 0
    engagement_shares: int = 0
    tags: List[str] = []
    is_read: bool = False

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    total: int
    page: int
    limit: int
    articles: List[ArticleResponse]


class StatsResponse(BaseModel):
    total_articles: int
    source_distribution: dict
    total_engagement: dict
    avg_score: float


class SourceResponse(BaseModel):
    id: str
    name: str
    type: str
    enabled: bool
    weight: float
    url: Optional[str] = None
    last_fetched_at: Optional[datetime] = None


class MessageResponse(BaseModel):
    message: str


def article_to_response(article: Article) -> ArticleResponse:
    return ArticleResponse(
        id=article.id,
        title=article.title,
        title_raw=article.title_raw,
        url=article.url,
        summary=article.summary,
        content=article.content,
        source=article.source,
        source_name=article.source_name,
        author=article.author,
        published_at=article.published_at,
        fetched_at=article.fetched_at,
        score=article.score,
        hotness=article.hotness,
        engagement_comments=article.engagement.comments,
        engagement_likes=article.engagement.likes,
        engagement_shares=article.engagement.shares,
        tags=article.tags,
        is_read=article.is_read
    )


@app.get("/")
async def root():
    return {"message": "Horizon API", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/articles", response_model=ArticleListResponse)
async def get_articles(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    source: Optional[str] = None,
    tag: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    sort: str = Query("hotness", regex="^(hotness|score|time)$")
):
    agg = get_aggregator()
    articles = agg.get_articles(
        page=page,
        limit=limit,
        source=source,
        tag=tag,
        date_from=date_from,
        date_to=date_to,
        sort=sort
    )
    
    return ArticleListResponse(
        total=len(articles),
        page=page,
        limit=limit,
        articles=[article_to_response(a) for a in articles]
    )


@app.get("/api/articles/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: str):
    agg = get_aggregator()
    article = agg.get_article_by_id(article_id)
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return article_to_response(article)


@app.post("/api/articles/{article_id}/read", response_model=MessageResponse)
async def mark_article_read(article_id: str):
    agg = get_aggregator()
    success = agg.mark_article_read(article_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return MessageResponse(message="Article marked as read")


@app.get("/api/sources", response_model=List[SourceResponse])
async def get_sources():
    agg = get_aggregator()
    sources = agg.config_loader.get_enabled_sources()
    
    return [
        SourceResponse(
            id=s.id,
            name=s.name,
            type=s.type.value if hasattr(s.type, 'value') else str(s.type),
            enabled=s.enabled,
            weight=s.weight,
            url=s.url,
            last_fetched_at=s.last_fetched_at
        )
        for s in sources
    ]


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats(days: int = Query(7, ge=1, le=90)):
    agg = get_aggregator()
    date_from = datetime.now() - timedelta(days=days)
    articles = agg.get_articles(
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
    
    return StatsResponse(
        total_articles=len(articles),
        source_distribution=source_counts,
        total_engagement=total_engagement,
        avg_score=sum(a.score for a in articles) / len(articles) if articles else 0
    )


@app.get("/api/trends")
async def get_trends(days: int = Query(30, ge=1, le=90)):
    agg = get_aggregator()
    date_from = datetime.now() - timedelta(days=days)
    articles = agg.get_articles(
        page=1,
        limit=1000,
        date_from=date_from,
        sort="hotness"
    )
    
    daily_counts = {}
    for article in articles:
        if article.published_at:
            date_key = article.published_at.strftime("%Y-%m-%d")
            daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
    
    return {
        "daily_article_counts": daily_counts,
        "total_articles": len(articles)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
