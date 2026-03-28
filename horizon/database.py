"""Database layer for Horizon"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from .models import Article, Source, Summary, Engagement

Base = declarative_base()


class ArticleDB(Base):
    """Article database model"""
    __tablename__ = "articles"
    
    id = Column(String, primary_key=True)
    title = Column(Text)
    title_raw = Column(Text)
    url = Column(String, unique=True)
    url_normalized = Column(String)
    summary = Column(Text)
    content = Column(Text)
    content_raw = Column(Text)
    source = Column(String)
    source_name = Column(String)
    author = Column(String)
    published_at = Column(DateTime)
    fetched_at = Column(DateTime)
    score = Column(Float, default=0)
    hotness = Column(Float, default=0)
    engagement_comments = Column(Integer, default=0)
    engagement_likes = Column(Integer, default=0)
    engagement_shares = Column(Integer, default=0)
    tags = Column(Text)
    is_read = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    md5_hash = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class SourceDB(Base):
    """Source database model"""
    __tablename__ = "sources"
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    type = Column(String)
    enabled = Column(Boolean, default=True)
    url = Column(String)
    auth_type = Column(String, default="none")
    auth_config = Column(Text)
    weight = Column(Float, default=5.0)
    timeout = Column(Integer, default=30)
    retry_times = Column(Integer, default=3)
    failure_count = Column(Integer, default=0)
    last_fetched_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)


class SummaryDB(Base):
    """Summary database model"""
    __tablename__ = "summaries"
    
    id = Column(String, primary_key=True)
    date = Column(String, unique=True)
    content = Column(Text)
    article_count = Column(Integer, default=0)
    sources = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class Database:
    """Database manager"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or self._get_default_db_path()
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._init_db()
    
    def _get_default_db_path(self) -> str:
        """Get default database path"""
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        return str(data_dir / "horizon.db")
    
    def _init_db(self) -> None:
        """Initialize database"""
        Base.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def save_article(self, article: Article) -> bool:
        """Save or update article"""
        session = self.get_session()
        try:
            existing = session.query(ArticleDB).filter(
                ArticleDB.url == article.url
            ).first()
            
            if existing:
                return False
            
            db_article = ArticleDB(
                id=article.id,
                title=article.title,
                title_raw=article.title_raw,
                url=article.url,
                url_normalized=article.url_normalized,
                summary=article.summary,
                content=article.content,
                content_raw=article.content_raw,
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
                tags=json.dumps(article.tags),
                is_read=article.is_read,
                is_archived=article.is_archived,
                md5_hash=article.md5_hash
            )
            session.add(db_article)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    
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
        """Get articles with filters"""
        session = self.get_session()
        try:
            query = session.query(ArticleDB)
            
            if source:
                sources = source.split(",")
                query = query.filter(ArticleDB.source.in_(sources))
            
            if tag:
                query = query.filter(ArticleDB.tags.like(f"%{tag}%"))
            
            if date_from:
                query = query.filter(ArticleDB.published_at >= date_from)
            
            if date_to:
                query = query.filter(ArticleDB.published_at <= date_to)
            
            if sort == "hotness":
                query = query.order_by(ArticleDB.hotness.desc())
            elif sort == "score":
                query = query.order_by(ArticleDB.score.desc())
            else:
                query = query.order_by(ArticleDB.published_at.desc())
            
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)
            
            articles = []
            for row in query.all():
                articles.append(self._row_to_article(row))
            
            return articles
        finally:
            session.close()
    
    def get_article_by_id(self, article_id: str) -> Optional[Article]:
        """Get article by ID"""
        session = self.get_session()
        try:
            row = session.query(ArticleDB).filter(
                ArticleDB.id == article_id
            ).first()
            return self._row_to_article(row) if row else None
        finally:
            session.close()
    
    def mark_article_read(self, article_id: str) -> bool:
        """Mark article as read"""
        session = self.get_session()
        try:
            article = session.query(ArticleDB).filter(
                ArticleDB.id == article_id
            ).first()
            if article:
                article.is_read = True
                session.commit()
                return True
            return False
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    
    def _row_to_article(self, row: ArticleDB) -> Article:
        """Convert database row to Article model"""
        return Article(
            id=row.id,
            title=row.title or "",
            title_raw=row.title_raw or "",
            url=row.url or "",
            url_normalized=row.url_normalized or "",
            summary=row.summary or "",
            content=row.content or "",
            content_raw=row.content_raw or "",
            source=row.source or "",
            source_name=row.source_name or "",
            author=row.author or "",
            published_at=row.published_at,
            fetched_at=row.fetched_at,
            score=row.score or 0.0,
            hotness=row.hotness or 0.0,
            engagement=Engagement(
                comments=row.engagement_comments or 0,
                likes=row.engagement_likes or 0,
                shares=row.engagement_shares or 0
            ),
            tags=json.loads(row.tags) if row.tags else [],
            is_read=row.is_read or False,
            is_archived=row.is_archived or False,
            md5_hash=row.md5_hash or ""
        )
