import React, { useState, useEffect } from 'react';
import { screenshotsAPI, getImageUrl } from '../services/api';

function Timeline() {
  const [screenshots, setScreenshots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedImage, setSelectedImage] = useState(null);

  const limit = 20;

  useEffect(() => {
    loadScreenshots();
  }, [page, selectedDate]);

  const loadScreenshots = async () => {
    setLoading(true);
    try {
      const response = await screenshotsAPI.getScreenshots({
        skip: page * limit,
        limit: limit,
        start_date: `${selectedDate}T00:00:00+08:00`,
        end_date: `${selectedDate}T23:59:59+08:00`,
      });
      
      setScreenshots(response.data.items);
      setTotal(response.data.total);
    } catch (error) {
      console.error('Error loading screenshots:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">时间轴</h1>
        <input
          type="date"
          className="input input-bordered"
          value={selectedDate}
          onChange={(e) => {
            setSelectedDate(e.target.value);
            setPage(0);
          }}
        />
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-96">
          <span className="loading loading-spinner loading-lg"></span>
        </div>
      ) : screenshots.length > 0 ? (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {screenshots.map((screenshot) => (
              <div
                key={screenshot.id}
                className="card bg-base-100 shadow-xl cursor-pointer hover:shadow-2xl transition-shadow"
                onClick={() => setSelectedImage(screenshot)}
              >
                <figure className="px-4 pt-4">
                  <img
                    src={getImageUrl(screenshot.thumbnail_url)}
                    alt={screenshot.filename}
                    className="rounded-xl w-full h-40 object-cover"
                  />
                </figure>
                <div className="card-body p-4">
                  <p className="text-xs text-gray-500">
                    {new Date(screenshot.timestamp).toLocaleTimeString('zh-CN', {
                      timeZone: 'Asia/Shanghai',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                  <div className="flex gap-2">
                    {screenshot.is_analyzed && (
                      <div className="badge badge-success badge-sm">已分析</div>
                    )}
                    {screenshot.is_similar && (
                      <div className="badge badge-warning badge-sm">相似</div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* 分页 */}
          <div className="flex justify-center">
            <div className="join">
              <button
                className="join-item btn"
                onClick={() => setPage(Math.max(0, page - 1))}
                disabled={page === 0}
              >
                «
              </button>
              <button className="join-item btn">
                页 {page + 1} / {totalPages}
              </button>
              <button
                className="join-item btn"
                onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                disabled={page >= totalPages - 1}
              >
                »
              </button>
            </div>
          </div>
        </>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-500">该日期暂无截屏记录</p>
        </div>
      )}

      {/* 图片预览模态框 */}
      {selectedImage && (
        <div className="modal modal-open">
          <div className="modal-box max-w-4xl">
            <h3 className="font-bold text-lg mb-4">
              {new Date(selectedImage.timestamp).toLocaleString('zh-CN', {
                timeZone: 'Asia/Shanghai'
              })}
            </h3>
            <img
              src={getImageUrl(`/files/${selectedImage.filename}`)}
              alt={selectedImage.filename}
              className="w-full rounded-lg"
            />
            <div className="modal-action">
              <button className="btn" onClick={() => setSelectedImage(null)}>
                关闭
              </button>
            </div>
          </div>
          <div className="modal-backdrop" onClick={() => setSelectedImage(null)}></div>
        </div>
      )}
    </div>
  );
}

export default Timeline;
