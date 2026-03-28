'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import dayjs from 'dayjs';
import { getArticles, getSources, markArticleRead } from '@/lib/api';
import type { Article, Source } from '@/types';

export default function HomePage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState('hotness');
  const [selectedSource, setSelectedSource] = useState('');

  useEffect(() => {
    loadData();
  }, [page, sort, selectedSource]);

  async function loadData() {
    setLoading(true);
    try {
      const [articlesRes, sourcesRes] = await Promise.all([
        getArticles({ page, limit: 20, sort, source: selectedSource }),
        getSources()
      ]);
      setArticles(articlesRes.articles);
      setSources(sourcesRes);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
    setLoading(false);
  }

  async function handleRead(id: string) {
    try {
      await markArticleRead(id);
      setArticles(articles.map(a => 
        a.id === id ? { ...a, is_read: true } : a
      ));
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  }

  function copyShareLink(url: string, title: string) {
    const shareUrl = `${window.location.origin}/article/${url}?utm_source=share`;
    navigator.clipboard.writeText(shareUrl);
    alert('链接已复制到剪贴板');
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">最新资讯</h2>
        <div className="flex gap-4">
          <select
            value={selectedSource}
            onChange={(e) => setSelectedSource(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">全部来源</option>
            {sources.map(s => (
              <option key={s.id} value={s.name}>{s.name}</option>
            ))}
          </select>
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg"
          >
            <option value="hotness">热度</option>
            <option value="score">评分</option>
            <option value="time">时间</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">加载中...</div>
      ) : articles.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          暂无资讯，请先运行 `horizon fetch` 抓取数据
        </div>
      ) : (
        <div className="grid gap-4">
          {articles.map((article) => (
            <article
              key={article.id}
              className={`article-card ${article.is_read ? 'opacity-60' : ''}`}
            >
              <Link href={`/article/${article.id}`}>
                <h3 className="article-title">{article.title}</h3>
              </Link>
              
              <div className="article-meta">
                <span className="text-blue-600">{article.source_name}</span>
                <span>|</span>
                {article.published_at && (
                  <span>{dayjs(article.published_at).format('YYYY-MM-DD HH:mm')}</span>
                )}
                <span>|</span>
                <span>评分: {article.score.toFixed(1)}</span>
                <span>|</span>
                <span>热度: {article.hotness.toFixed(0)}</span>
              </div>
              
              <p className="text-gray-600 mt-2 line-clamp-2">
                {article.summary && article.summary !== article.title 
                  ? article.summary 
                  : '点击"原文"链接查看完整内容'}
              </p>
              
              <div className="flex gap-2 mt-3">
                {article.tags.map(tag => (
                  <span key={tag} className="tag">{tag}</span>
                ))}
              </div>
              
              <div className="flex gap-2 mt-3">
                <button
                  onClick={() => handleRead(article.id)}
                  className="text-sm text-gray-500 hover:text-blue-600"
                >
                  {article.is_read ? '已读' : '标记已读'}
                </button>
                <button
                  onClick={() => copyShareLink(article.id, article.title)}
                  className="text-sm text-gray-500 hover:text-blue-600"
                >
                  分享
                </button>
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-gray-500 hover:text-blue-600"
                >
                  原文
                </a>
              </div>
            </article>
          ))}
        </div>
      )}

      <div className="flex justify-center gap-4 mt-8">
        <button
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50"
        >
          上一页
        </button>
        <span className="px-4 py-2">第 {page} 页</span>
        <button
          onClick={() => setPage(p => p + 1)}
          disabled={articles.length < 20}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50"
        >
          下一页
        </button>
      </div>
    </div>
  );
}
