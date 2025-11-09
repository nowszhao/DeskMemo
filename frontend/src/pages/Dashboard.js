import React, { useState, useEffect } from 'react';
import { statsAPI, activitiesAPI } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const COLORS = {
  '工作': '#0088FE',
  '学习': '#00C49F',
  '娱乐': '#FFBB28',
  '其他': '#FF8042',
};

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recentActivities, setRecentActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 60000); // 每分钟刷新
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, activitiesRes] = await Promise.all([
        statsAPI.getTodayStats(),
        activitiesAPI.getActivities({ limit: 10 })
      ]);
      
      setStats(statsRes.data);
      setRecentActivities(activitiesRes.data.items);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  const chartData = stats?.activity_distribution
    ? Object.entries(stats.activity_distribution).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">今日概览</h1>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="stat bg-base-100 shadow">
          <div className="stat-title">截屏总数</div>
          <div className="stat-value text-primary">{stats?.screenshot_count || 0}</div>
          <div className="stat-desc">自动捕获</div>
        </div>

        <div className="stat bg-base-100 shadow">
          <div className="stat-title">活动记录</div>
          <div className="stat-value text-secondary">{stats?.activity_count || 0}</div>
          <div className="stat-desc">已分析</div>
        </div>

        <div className="stat bg-base-100 shadow">
          <div className="stat-title">已分析</div>
          <div className="stat-value">{stats?.analyzed_count || 0}</div>
          <div className="stat-desc">AI 解析完成</div>
        </div>

        <div className="stat bg-base-100 shadow">
          <div className="stat-title">日期</div>
          <div className="stat-value text-sm">{stats?.date || new Date().toLocaleDateString()}</div>
          <div className="stat-desc">实时更新</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 活动分布图 */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title">活动类型分布</h2>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#999'} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex justify-center items-center h-64">
                <p className="text-gray-500">暂无数据</p>
              </div>
            )}
          </div>
        </div>

        {/* 最近活动 */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title">最近活动</h2>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {recentActivities.length > 0 ? (
                recentActivities.map((activity) => (
                  <div key={activity.id} className="border-l-4 border-primary pl-4 py-2">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="badge badge-sm badge-outline mb-1">
                          {activity.activity_type}
                        </div>
                        <p className="text-sm">{activity.description}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {activity.application}
                        </p>
                      </div>
                      <div className="text-xs text-gray-400">
                        {new Date(activity.timestamp).toLocaleTimeString('zh-CN', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-8">暂无活动记录</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
