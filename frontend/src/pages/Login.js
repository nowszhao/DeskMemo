import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';

function Login({ onLoginSuccess }) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authAPI.login(password);
      
      if (response.data.success) {
        // 保存 token
        if (response.data.token) {
          localStorage.setItem('auth_token', response.data.token);
        }
        
        // 通知父组件登录成功
        onLoginSuccess();
        
        // 跳转到首页
        navigate('/');
      }
    } catch (err) {
      setError(err.response?.data?.detail || '登录失败，请检查密码');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-base-200">
      <div className="card w-96 bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title justify-center text-2xl mb-4">
            📊 桌面记忆
          </h2>
          <p className="text-center text-sm opacity-70 mb-4">
            请输入密码以继续
          </p>
          
          <form onSubmit={handleSubmit}>
            <div className="form-control">
              <label className="label">
                <span className="label-text">密码</span>
              </label>
              <input
                type="password"
                placeholder="请输入密码"
                className="input input-bordered"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                autoFocus
              />
            </div>

            {error && (
              <div className="alert alert-error mt-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{error}</span>
              </div>
            )}

            <div className="form-control mt-6">
              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={loading || !password}
              >
                {loading ? (
                  <>
                    <span className="loading loading-spinner"></span>
                    登录中...
                  </>
                ) : '登录'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Login;
