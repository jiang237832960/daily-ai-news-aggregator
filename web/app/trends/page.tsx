'use client';

import { useState, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';
import { getTrends, getStats } from '@/lib/api';
import type { TrendData, Stats } from '@/types';

export default function TrendsPage() {
  const [trendData, setTrendData] = useState<TrendData | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  useEffect(() => {
    loadData();
  }, [days]);

  async function loadData() {
    setLoading(true);
    try {
      const [trendRes, statsRes] = await Promise.all([
        getTrends(days),
        getStats(days)
      ]);
      setTrendData(trendRes);
      setStats(statsRes);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
    setLoading(false);
  }

  function getDailyChartOption() {
    if (!trendData?.daily_article_counts) return {};
    
    const dates = Object.keys(trendData.daily_article_counts).sort();
    const counts = dates.map(d => trendData.daily_article_counts[d]);
    
    return {
      title: {
        text: '每日文章发布量',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: dates.map(d => dayjs(d).format('MM-DD')),
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        name: '文章数量'
      },
      series: [
        {
          name: '文章数量',
          type: 'line',
          data: counts,
          smooth: true,
          areaStyle: {
            color: 'rgba(59, 130, 246, 0.2)'
          },
          lineStyle: {
            color: '#3b82f6'
          },
          itemStyle: {
            color: '#3b82f6'
          }
        }
      ]
    };
  }

  function getSourceChartOption() {
    if (!stats?.source_distribution) return {};
    
    const data = Object.entries(stats.source_distribution)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
    
    return {
      title: {
        text: '来源分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item'
      },
      series: [
        {
          name: '文章数量',
          type: 'pie',
          radius: '60%',
          data: data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    };
  }

  if (loading) {
    return <div className="text-center py-12">加载中...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">趋势分析</h2>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="px-3 py-2 border border-gray-300 rounded-lg"
        >
          <option value={7}>最近7天</option>
          <option value={14}>最近14天</option>
          <option value={30}>最近30天</option>
          <option value={60}>最近60天</option>
        </select>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-4">
          <div className="text-sm text-gray-500">总文章数</div>
          <div className="text-3xl font-bold text-blue-600">
            {stats?.total_articles ?? 0}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-4">
          <div className="text-sm text-gray-500">平均评分</div>
          <div className="text-3xl font-bold text-green-600">
            {stats?.avg_score.toFixed(1) ?? '0.0'}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-4">
          <div className="text-sm text-gray-500">总评论数</div>
          <div className="text-3xl font-bold text-purple-600">
            {stats?.total_engagement.comments ?? 0}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-4">
          <div className="text-sm text-gray-500">总点赞数</div>
          <div className="text-3xl font-bold text-red-600">
            {stats?.total_engagement.likes ?? 0}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-4">
          <ReactECharts option={getDailyChartOption()} style={{ height: 400 }} />
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-4">
          <ReactECharts option={getSourceChartOption()} style={{ height: 400 }} />
        </div>
      </div>
    </div>
  );
}
