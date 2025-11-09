import React, { useState } from 'react';
import { searchAPI, getImageUrl } from '../services/api';

function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setSearched(true);
    try {
      const response = await searchAPI.search(query, 20);
      setResults(response.data.items);
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">活动搜索</h1>

      {/* 搜索框 */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          placeholder="输入关键词或描述搜索活动..."
          className="input input-bordered flex-1"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? (
            <span className="loading loading-spinner"></span>
          ) : (
            '搜索'
          )}
        </button>
      </form>

      {/* 搜索提示 */}
      {!searched && (
        <div className="alert alert-info">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span>支持关键词搜索和语义搜索。例如：搜索"写代码"、"看视频"、"浏览网页"等</span>
        </div>
      )}

      {/* 搜索结果 */}
      {loading ? (
        <div className="flex justify-center items-center h-96">
          <span className="loading loading-spinner loading-lg"></span>
        </div>
      ) : searched && (
        <>
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">
              找到 {results.length} 条结果
            </h2>
          </div>

          {results.length > 0 ? (
            <div className="space-y-4">
              {results.map((result) => (
                <div key={result.id} className="card bg-base-100 shadow-xl">
                  <div className="card-body">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex gap-2 mb-2">
                          <div className="badge badge-primary">{result.activity_type}</div>
                          <div className="badge badge-outline">
                            {result.relevance === 'semantic' ? '语义匹配' : '关键词匹配'}
                          </div>
                          {result.score && (
                            <div className="badge badge-ghost">
                              相关度: {(result.score * 100).toFixed(0)}%
                            </div>
                          )}
                        </div>
                        <h3 className="font-semibold text-lg mb-2">{result.description}</h3>
                        <p className="text-sm text-gray-600 mb-2">
                          应用：{result.application}
                        </p>
                        <p className="text-xs text-gray-500">
                          时间：{new Date(result.timestamp).toLocaleString('zh-CN', {
                            timeZone: 'Asia/Shanghai'
                          })}
                        </p>
                      </div>
                      {result.screenshot_filename && (
                        <img
                          src={getImageUrl(`/files/thumbnails/thumb_${result.screenshot_filename}`)}
                          alt="截图"
                          className="w-32 h-24 object-cover rounded-lg ml-4"
                        />
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">未找到相关结果</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Search;
