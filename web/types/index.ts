export interface Article {
  id: string;
  title: string;
  title_raw?: string;
  url: string;
  summary: string;
  content?: string;
  source: string;
  source_name: string;
  author: string;
  published_at?: string;
  fetched_at: string;
  score: number;
  hotness: number;
  engagement_comments: number;
  engagement_likes: number;
  engagement_shares: number;
  tags: string[];
  is_read: boolean;
}

export interface ArticleListResponse {
  total: number;
  page: number;
  limit: number;
  articles: Article[];
}

export interface Source {
  id: string;
  name: string;
  type: string;
  enabled: boolean;
  weight: number;
  url?: string;
  last_fetched_at?: string;
}

export interface Stats {
  total_articles: number;
  source_distribution: Record<string, number>;
  total_engagement: {
    comments: number;
    likes: number;
    shares: number;
  };
  avg_score: number;
}

export interface TrendData {
  daily_article_counts: Record<string, number>;
  total_articles: number;
}
