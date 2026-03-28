import axios from 'axios';
import type { Article, ArticleListResponse, Source, Stats, TrendData } from '@/types';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

export async function getArticles(params: {
  page?: number;
  limit?: number;
  source?: string;
  tag?: string;
  sort?: string;
}): Promise<ArticleListResponse> {
  const { data } = await api.get('/articles', { params });
  return data;
}

export async function getArticle(id: string): Promise<Article> {
  const { data } = await api.get(`/articles/${id}`);
  return data;
}

export async function markArticleRead(id: string): Promise<void> {
  await api.post(`/articles/${id}/read`);
}

export async function getSources(): Promise<Source[]> {
  const { data } = await api.get('/sources');
  return data;
}

export async function getStats(days: number = 7): Promise<Stats> {
  const { data } = await api.get('/stats', { params: { days } });
  return data;
}

export async function getTrends(days: number = 30): Promise<TrendData> {
  const { data } = await api.get('/trends', { params: { days } });
  return data;
}
