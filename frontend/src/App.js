import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useNavigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Timeline from './pages/Timeline';
import Reports from './pages/Reports';
import Search from './pages/Search';
import Login from './pages/Login';
import { authAPI } from './services/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(null); // null = 未检查, true/false = 已检查
  const [authEnabled, setAuthEnabled] = useState(false);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await authAPI.checkAuth();
      const authEnabledValue = response.data.auth_enabled;
      setAuthEnabled(authEnabledValue);
      
      // 如果未启用认证，直接标记为已认证
      if (!authEnabledValue) {
        setIsAuthenticated(true);
      } else {
        // 如果启用了认证，检查是否有 token
        const token = localStorage.getItem('auth_token');
        setIsAuthenticated(!!token);
      }
    } catch (error) {
      console.error('检查认证状态失败:', error);
      // 检查失败时，假设需要认证
      setAuthEnabled(true);
      setIsAuthenticated(false);
    }
  };

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('登出失败:', error);
    }
    localStorage.removeItem('auth_token');
    setIsAuthenticated(false);
  };

  // 等待认证状态检查完成
  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-base-200">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={
            !authEnabled || isAuthenticated ? (
              <Navigate to="/" replace />
            ) : (
              <Login onLoginSuccess={handleLoginSuccess} />
            )
          } 
        />
        
        <Route
          path="/*"
          element={
            authEnabled && !isAuthenticated ? (
              <Navigate to="/login" replace />
            ) : (
              <MainLayout onLogout={handleLogout} authEnabled={authEnabled} />
            )
          }
        />
      </Routes>
    </Router>
  );
}

function MainLayout({ onLogout, authEnabled }) {
  return (
    <div className="min-h-screen bg-base-200">
      {/* 导航栏 */}
      <div className="navbar bg-base-100 shadow-lg">
        <div className="flex-1">
          <Link to="/" className="btn btn-ghost normal-case text-xl">
            📊 桌面记忆
          </Link>
        </div>
        <div className="flex-none">
          <ul className="menu menu-horizontal px-1">
            <li><Link to="/">仪表盘</Link></li>
            <li><Link to="/timeline">时间轴</Link></li>
            <li><Link to="/reports">报告</Link></li>
            <li><Link to="/search">搜索</Link></li>
            {authEnabled && (
              <li>
                <button onClick={onLogout} className="btn btn-ghost btn-sm">
                  登出
                </button>
              </li>
            )}
          </ul>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="container mx-auto p-4">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/timeline" element={<Timeline />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/search" element={<Search />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
