'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import dayjs from 'dayjs';
import { getArticle, markArticleRead } from '@/lib/api';
import type { Article } from '@/types';

export default function ArticlePage() {
  const params = useParams();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      loadArticle(params.id as string);
    }
  }, [params.id]);

  async function loadArticle(id: string) {
    setLoading(true);
    try {
      const data = await getArticle(id);
      setArticle(data);
      if (!data.is_read) {
        markArticleRead(id);
      }
    } catch (error) {
      console.error('Failed to load article:', error);
    }
    setLoading(false);
  }

  if (loading) {
    return <div className="text-center py-12">加载中...</div>;
  }

  if (!article) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-800">文章未找到</h2>
        <Link href="/" className="text-blue-600 hover:underline mt-4 inline-block">
          返回首页
        </Link>
      </div>
    );
  }

  return (
    <div>
      <Link href="/" className="text-blue-600 hover:underline mb-4 inline-block">
        &larr; 返回首页
      </Link>
      
      <article className="bg-white rounded-lg shadow-sm border border-gray-100 p-8">
        <header className="mb-8 pb-6 border-b border-gray-200">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">{article.title}</h1>
          
          <div className="flex flex-wrap gap-4 text-sm text-gray-500">
            <span className="text-blue-600 font-medium">{article.source_name}</span>
            {article.author && <span>作者: {article.author}</span>}
            {article.published_at && (
              <span>{dayjs(article.published_at).format('YYYY-MM-DD HH:mm')}</span>
            )}
            <span>评分: {article.score.toFixed(1)}</span>
            <span>热度: {article.hotness.toFixed(0)}</span>
          </div>
          
          <div className="flex gap-2 mt-4">
            {article.tags.map(tag => (
              <span key={tag} className="tag">{tag}</span>
            ))}
          </div>
        </header>
        
        <div className="prose max-w-none">
          {article.summary && article.summary !== article.title ? (
            <p className="text-lg text-gray-700 leading-relaxed mb-6">
              {article.summary}
            </p>
          ) : (
            <div className="bg-blue-50 rounded-lg p-4 mb-6">
              <p className="text-blue-800">
                此文章来自 {article.source_name}，点击下方"阅读原文"按钮查看完整内容。
              </p>
            </div>
          )}
          
          {article.content && (
            <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
              {article.content}
            </div>
          )}
        </div>
        
        <footer className="mt-8 pt-6 border-t border-gray-200">
          <div className="flex gap-4">
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              阅读原文
            </a>
            <button
              onClick={() => {
                const shareUrl = `${window.location.origin}/article/${article.id}?utm_source=share`;
                navigator.clipboard.writeText(shareUrl);
                alert('链接已复制');
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              分享文章
            </button>
          </div>
          
          <div className="mt-6 text-sm text-gray-500">
            <span>评论: {article.engagement_comments}</span>
            <span className="mx-3">|</span>
            <span>点赞: {article.engagement_likes}</span>
            <span className="mx-3">|</span>
            <span>分享: {article.engagement_shares}</span>
          </div>
        </footer>
      </article>
    </div>
  );
}
