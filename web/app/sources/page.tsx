'use client';

import { useState, useEffect } from 'react';
import { getSources } from '@/lib/api';
import type { Source } from '@/types';

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSources();
  }, []);

  async function loadSources() {
    setLoading(true);
    try {
      const data = await getSources();
      setSources(data);
    } catch (error) {
      console.error('Failed to load sources:', error);
    }
    setLoading(false);
  }

  function getTypeColor(type: string) {
    const colors: Record<string, string> = {
      hackernews: 'bg-orange-100 text-orange-700',
      reddit: 'bg-red-100 text-red-700',
      arxiv: 'bg-green-100 text-green-700',
      github: 'bg-gray-800 text-white',
      rss: 'bg-blue-100 text-blue-700',
      lobsters: 'bg-teal-100 text-teal-700',
      youtube: 'bg-red-600 text-white',
    };
    return colors[type] || 'bg-gray-100 text-gray-700';
  }

  if (loading) {
    return <div className="text-center py-12">加载中...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">来源管理</h2>
        <span className="text-sm text-gray-500">
          共 {sources.length} 个来源，{sources.filter(s => s.enabled).length} 个已启用
        </span>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                来源
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                类型
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                权重
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                状态
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                上次抓取
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {sources.map((source) => (
              <tr key={source.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="font-medium text-gray-900">{source.name}</div>
                  {source.url && (
                    <div className="text-sm text-gray-500 truncate max-w-xs">
                      {source.url}
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs rounded-full ${getTypeColor(source.type)}`}>
                    {source.type}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-24 h-2 bg-gray-200 rounded-full mr-2">
                      <div
                        className="h-2 bg-blue-600 rounded-full"
                        style={{ width: `${source.weight * 10}%` }}
                      />
                    </div>
                    <span className="text-sm text-gray-600">{source.weight.toFixed(1)}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {source.enabled ? (
                    <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-700">
                      已启用
                    </span>
                  ) : (
                    <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-600">
                      已禁用
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {source.last_fetched_at
                    ? new Date(source.last_fetched_at).toLocaleString('zh-CN')
                    : '从未抓取'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-6 bg-blue-50 rounded-lg p-4">
        <h3 className="font-medium text-blue-800 mb-2">管理来源</h3>
        <p className="text-sm text-blue-600">
          编辑 <code className="bg-blue-100 px-1 rounded">data/config.json</code> 文件来添加、删除或修改来源配置。
          修改后需要重启应用。
        </p>
      </div>
    </div>
  );
}
