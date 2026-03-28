"""Translator for content translation"""

import asyncio
from typing import Optional

try:
    from googletrans import Translator as GoogleTranslator
    GOOGLE_TRANSLATE_AVAILABLE = True
except ImportError:
    GOOGLE_TRANSLATE_AVAILABLE = False

from .models import Article, Config


class Translator:
    """Translate content to Chinese"""
    
    def __init__(self, config: Config):
        self.config = config
        self.provider = config.translation.get("provider", "google")
        self.timeout = config.translation.get("timeout", 10)
        self.enabled = config.translation.get("enabled", True)
        self._google_translator: Optional[GoogleTranslator] = None
    
    async def translate(self, text: str, source_lang: str = 'en', target_lang: str = 'zh-cn') -> str:
        """Translate text to target language"""
        if not self.enabled or not text:
            return text
        
        if not self._is_english(text):
            return text
        
        try:
            if self.provider == "google" and GOOGLE_TRANSLATE_AVAILABLE:
                return await self._translate_google(text, source_lang, target_lang)
            else:
                return text
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    async def _translate_google(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """Translate using Google Translate"""
        if self._google_translator is None:
            self._google_translator = GoogleTranslator()
        
        try:
            result = await self._google_translator.translate(
                text,
                src=source_lang,
                dest=target_lang
            )
            return result.text if hasattr(result, 'text') else str(result)
        except Exception as e:
            try:
                result = self._google_translator.translate(text, src=source_lang, dest=target_lang)
                return result.text if hasattr(result, 'text') else str(result)
            except Exception:
                return text
    
    async def translate_article(self, article: Article) -> Article:
        """Translate article content"""
        if not self.enabled:
            return article
        
        if self._is_english(article.title_raw or article.title):
            article.title = await self.translate(
                article.title_raw or article.title
            )
        
        if article.content and self._is_english(article.content):
            article.content = await self.translate(article.content)
        
        if article.summary and self._is_english(article.summary):
            article.summary = await self.translate(article.summary)
        
        return article
    
    def _is_english(self, text: str) -> bool:
        """Check if text is primarily English"""
        if not text:
            return False
        
        english_chars = sum(1 for c in text if c.isascii())
        total_chars = len(text.strip())
        
        if total_chars == 0:
            return False
        
        return english_chars / total_chars > 0.8
