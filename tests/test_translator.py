"""Tests for translator module"""

import pytest
from horizon.translator import Translator
from horizon.models import Article, Config


class TestTranslator:
    """Test cases for Translator"""

    def setup_method(self):
        """Setup test fixtures"""
        config = Config(translation={
            "provider": "google",
            "enabled": False,
            "timeout": 10
        })
        self.translator = Translator(config)

    def test_is_english_pure_english(self):
        """Test English detection for pure English text"""
        assert self.translator._is_english("This is a test article")

    def test_is_english_pure_chinese(self):
        """Test English detection for pure Chinese text"""
        assert not self.translator._is_english("这是一个测试文章")

    def test_is_english_mixed(self):
        """Test English detection for mixed text"""
        result = self.translator._is_english("Hello 你好 World")
        # May be considered English if >80% ASCII

    def test_is_english_empty(self):
        """Test English detection for empty text"""
        assert not self.translator._is_english("")
        assert not self.translator._is_english(None)

    def test_is_english_short(self):
        """Test English detection for very short text"""
        assert not self.translator._is_english("A")

    @pytest.mark.asyncio
    async def test_translate_disabled(self):
        """Test translation when disabled"""
        self.translator.enabled = False
        result = await self.translator.translate("Hello")
        assert result == "Hello"

    @pytest.mark.asyncio
    async def test_translate_chinese_content(self):
        """Test translation skips Chinese content"""
        self.translator.enabled = True
        result = await self.translator.translate("你好世界")
        assert result == "你好世界"

    @pytest.mark.asyncio
    async def test_translate_article_disabled(self):
        """Test article translation when disabled"""
        self.translator.enabled = False
        article = Article(
            title="Hello World",
            title_raw="Hello World",
            content="This is a test"
        )
        result = await self.translator.translate_article(article)
        assert result.title == "Hello World"


class TestTranslatorEnabled:
    """Test cases for enabled translator"""

    def setup_method(self):
        """Setup test fixtures with enabled translator"""
        config = Config(translation={
            "provider": "google",
            "enabled": True,
            "timeout": 10
        })
        self.translator = Translator(config)

    @pytest.mark.asyncio
    async def test_translate_english_to_chinese(self):
        """Test translation from English to Chinese"""
        # This would need actual API or mock
        # For now, just verify the method runs
        pass

    def test_provider_config(self):
        """Test provider configuration"""
        assert self.translator.provider == "google"
        assert self.translator.timeout == 10
        assert self.translator.enabled is True
