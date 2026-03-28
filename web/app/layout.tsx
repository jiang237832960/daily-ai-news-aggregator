import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Horizon - AI资讯聚合',
  description: '自动获取每日最新AI资讯并翻译为中文',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="bg-gray-50 min-h-screen">
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-blue-600">Horizon</h1>
              <nav className="flex gap-6">
                <a href="/" className="text-gray-600 hover:text-blue-600">首页</a>
                <a href="/trends" className="text-gray-600 hover:text-blue-600">趋势</a>
                <a href="/sources" className="text-gray-600 hover:text-blue-600">来源</a>
              </nav>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
