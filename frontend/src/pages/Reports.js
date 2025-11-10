import React, { useState, useEffect } from 'react';
import { reportsAPI } from '../services/api';
import { getTodayBeijing } from '../utils/timezone';

function Reports() {
  const [activeTab, setActiveTab] = useState('hourly');
  const [hourlyReports, setHourlyReports] = useState([]);
  const [dailyReports, setDailyReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(getTodayBeijing());

  const loadReports = async () => {
    setLoading(true);
    try {
      if (activeTab === 'hourly') {
        const response = await reportsAPI.getHourlyReports(selectedDate);
        setHourlyReports(response.data.items);
      } else {
        const response = await reportsAPI.getDailyReports(7);
        setDailyReports(response.data.items);
      }
    } catch (error) {
      console.error('Error loading reports:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, selectedDate]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">工作报告</h1>
        {activeTab === 'hourly' && (
          <input
            type="date"
            className="input input-bordered"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
          />
        )}
      </div>

      {/* 标签页 */}
      <div className="tabs tabs-boxed">
        <a
          className={`tab ${activeTab === 'hourly' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('hourly')}
        >
          小时报告
        </a>
        <a
          className={`tab ${activeTab === 'daily' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('daily')}
        >
          日报
        </a>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-96">
          <span className="loading loading-spinner loading-lg"></span>
        </div>
      ) : (
        <div className="space-y-4">
          {activeTab === 'hourly' ? (
            hourlyReports.length > 0 ? (
              hourlyReports.map((report) => (
                <div key={report.id} className="card bg-base-100 shadow-xl">
                  <div className="card-body">
                    <h2 className="card-title">
                      {new Date(report.start_time).toLocaleTimeString('zh-CN', {
                        timeZone: 'Asia/Shanghai',
                        hour: '2-digit',
                        minute: '2-digit'
                      })} - {new Date(report.end_time).toLocaleTimeString('zh-CN', {
                        timeZone: 'Asia/Shanghai',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </h2>
                    <p className="whitespace-pre-wrap">{report.summary}</p>
                    
                    <div className="divider"></div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      <div className="stat place-items-center">
                        <div className="stat-title">截屏</div>
                        <div className="stat-value text-sm">{report.screenshot_count}</div>
                      </div>
                      <div className="stat place-items-center">
                        <div className="stat-title">工作</div>
                        <div className="stat-value text-sm text-primary">{report.work_minutes}分</div>
                      </div>
                      <div className="stat place-items-center">
                        <div className="stat-title">学习</div>
                        <div className="stat-value text-sm text-secondary">{report.study_minutes}分</div>
                      </div>
                      <div className="stat place-items-center">
                        <div className="stat-title">娱乐</div>
                        <div className="stat-value text-sm text-accent">{report.entertainment_minutes}分</div>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500">该日期暂无小时报告</p>
              </div>
            )
          ) : (
            dailyReports.length > 0 ? (
              dailyReports.map((report) => (
                <div key={report.id} className="card bg-base-100 shadow-xl">
                  <div className="card-body">
                    <h2 className="card-title">
                      {report.date} 日报
                    </h2>
                    <p className="whitespace-pre-wrap">{report.summary}</p>
                    
                    <div className="divider"></div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                      <div className="stat place-items-center">
                        <div className="stat-title">截屏</div>
                        <div className="stat-value text-sm">{report.screenshot_count}</div>
                      </div>
                      <div className="stat place-items-center">
                        <div className="stat-title">工作</div>
                        <div className="stat-value text-sm text-primary">{report.work_minutes}分</div>
                      </div>
                      <div className="stat place-items-center">
                        <div className="stat-title">学习</div>
                        <div className="stat-value text-sm text-secondary">{report.study_minutes}分</div>
                      </div>
                      <div className="stat place-items-center">
                        <div className="stat-title">娱乐</div>
                        <div className="stat-value text-sm text-accent">{report.entertainment_minutes}分</div>
                      </div>
                      <div className="stat place-items-center">
                        <div className="stat-title">其他</div>
                        <div className="stat-value text-sm">{report.other_minutes}分</div>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500">暂无日报</p>
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
}

export default Reports;
