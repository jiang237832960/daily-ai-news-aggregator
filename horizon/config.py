"""Configuration loader for Horizon"""

import json
import os
from pathlib import Path
from typing import Optional

from .models import Config, Source, SourceType


DEFAULT_CONFIG = {
    "version": 1,
    "translation": {
        "provider": "google",
        "enabled": True,
        "timeout": 10
    },
    "sources": [
        {
            "name": "HackerNews",
            "type": "hackernews",
            "enabled": True,
            "weight": 8.0,
            "timeout": 30
        },
        {
            "name": "Reddit ML",
            "type": "reddit",
            "enabled": False,
            "url": "r/machinelearning",
            "weight": 7.0
        },
        {
            "name": "ArXiv CS.AI",
            "type": "arxiv",
            "enabled": False,
            "url": "https://arxiv.org/rss/cs.AI",
            "weight": 8.0
        }
    ],
    "scoring": {
        "keywords": {
            "突发": 2, "重磅": 2, "首发": 2,
            "breaking": 2, "exclusive": 2
        },
        "length_bonus": {"min": 1000, "max": 10000, "score": 1},
        "freshness_hours": 24,
        "freshness_bonus": 2
    },
    "scheduler": {
        "enabled": False,
        "cron": "0 8 * * *",
        "timezone": "Asia/Shanghai"
    }
}


class ConfigLoader:
    """Load and manage configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._config: Optional[Config] = None
    
    def _get_default_config_path(self) -> Path:
        """Get default config path"""
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        return data_dir / "config.json"
    
    def load(self) -> Config:
        """Load configuration from file"""
        if self._config is not None:
            return self._config
        
        if not Path(self.config_path).exists():
            self._create_default_config()
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Configuration file format error: {e}")
        
        sources = []
        for src in data.get("sources", []):
            src_type = src.get("type", "rss")
            if isinstance(src_type, str):
                src_type = SourceType(src_type)
            sources.append(Source(
                name=src.get("name", ""),
                type=src_type,
                enabled=src.get("enabled", True),
                url=src.get("url", ""),
                auth_type=src.get("auth_type", "none"),
                auth_config=src.get("auth_config", {}),
                weight=src.get("weight", 5.0),
                timeout=src.get("timeout", 30),
                retry_times=src.get("retry_times", 3)
            ))
        
        self._config = Config(
            version=data.get("version", 1),
            translation=data.get("translation", DEFAULT_CONFIG["translation"]),
            sources=sources,
            scoring=data.get("scoring", DEFAULT_CONFIG["scoring"]),
            scheduler=data.get("scheduler", DEFAULT_CONFIG["scheduler"])
        )
        
        return self._config
    
    def _create_default_config(self) -> None:
        """Create default configuration file"""
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=4)
    
    def save(self, config: Config) -> None:
        """Save configuration to file"""
        data = {
            "version": config.version,
            "translation": config.translation,
            "sources": [
                {
                    "name": s.name,
                    "type": s.type.value if isinstance(s.type, SourceType) else s.type,
                    "enabled": s.enabled,
                    "url": s.url,
                    "auth_type": s.auth_type,
                    "auth_config": s.auth_config,
                    "weight": s.weight,
                    "timeout": s.timeout,
                    "retry_times": s.retry_times
                }
                for s in config.sources
            ],
            "scoring": config.scoring,
            "scheduler": config.scheduler
        }
        
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        self._config = config
    
    def get_source(self, name: str) -> Optional[Source]:
        """Get source by name"""
        config = self.load()
        for source in config.sources:
            if source.name == name:
                return source
        return None
    
    def get_enabled_sources(self) -> list[Source]:
        """Get all enabled sources"""
        config = self.load()
        return [s for s in config.sources if s.enabled]
