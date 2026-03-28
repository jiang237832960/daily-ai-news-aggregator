"""Data models for Horizon"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid


class SourceType(str, Enum):
    """Supported source types"""
    HACKERNEWS = "hackernews"
    RSS = "rss"
    REDDIT = "reddit"
    GITHUB = "github"
    ARXIV = "arxiv"
    LOBSTERS = "lobsters"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    STACKOVERFLOW = "stackoverflow"
    DEVCOM = "devcommunity"
    MEDIUM = "medium"
    WECHAT = "wechat"


class Engagement(BaseModel):
    """Engagement metrics"""
    comments: int = 0
    likes: int = 0
    shares: int = 0


class Article(BaseModel):
    """Article model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    title_raw: str = ""
    url: str = ""
    url_normalized: str = ""
    summary: str = ""
    content: str = ""
    content_raw: str = ""
    source: str = ""
    source_name: str = ""
    author: str = ""
    published_at: Optional[datetime] = None
    fetched_at: datetime = Field(default_factory=datetime.now)
    score: float = 0.0
    hotness: float = 0.0
    engagement: Engagement = Field(default_factory=Engagement)
    tags: List[str] = Field(default_factory=list)
    is_read: bool = False
    is_archived: bool = False
    md5_hash: str = ""
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Source(BaseModel):
    """Source configuration model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: SourceType
    enabled: bool = True
    url: str = ""
    auth_type: str = "none"
    auth_config: dict = Field(default_factory=dict)
    weight: float = 5.0
    timeout: int = 30
    retry_times: int = 3
    failure_count: int = 0
    last_fetched_at: Optional[datetime] = None


class Summary(BaseModel):
    """Daily summary model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str
    content: str = ""
    article_count: int = 0
    sources: List[str] = Field(default_factory=list)


class RawContent(BaseModel):
    """Raw content from crawler"""
    url: str
    title: str
    content: str
    author: str = ""
    published_at: Optional[datetime] = None
    fetched_at: datetime = Field(default_factory=datetime.now)
    engagement: Engagement = Field(default_factory=Engagement)
    raw_data: dict = Field(default_factory=dict)


class Config(BaseModel):
    """Application configuration"""
    version: int = 1
    translation: dict = Field(default_factory=lambda: {
        "provider": "google",
        "enabled": True,
        "timeout": 10
    })
    sources: List[Source] = Field(default_factory=list)
    scoring: dict = Field(default_factory=lambda: {
        "keywords": {
            "突发": 2, "重磅": 2, "首发": 2,
            "breaking": 2, "exclusive": 2
        },
        "length_bonus": {"min": 1000, "max": 10000, "score": 1},
        "freshness_hours": 24,
        "freshness_bonus": 2
    })
    scheduler: dict = Field(default_factory=lambda: {
        "enabled": False,
        "cron": "0 8 * * *",
        "timezone": "Asia/Shanghai"
    })
