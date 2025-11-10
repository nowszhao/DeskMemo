/**
 * 时区工具函数
 * 统一使用北京时间（Asia/Shanghai）
 */

/**
 * 获取北京时间的今天日期字符串 (YYYY-MM-DD)
 */
export const getTodayBeijing = () => {
  // 使用 toLocaleDateString 直接获取北京时区的日期
  return new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Shanghai' });
};

/**
 * 获取北京时间的当前时间
 */
export const getNowBeijing = () => {
  // 手动计算北京时间（UTC+8）
  const now = new Date();
  const utcTime = now.getTime() + (now.getTimezoneOffset() * 60000);
  return new Date(utcTime + (3600000 * 8));
};

/**
 * 格式化日期为北京时间
 * @param {Date|string} date - 日期对象或ISO字符串
 * @param {Object} options - Intl.DateTimeFormat 选项
 */
export const formatBeijingTime = (date, options = {}) => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    ...options
  });
};

/**
 * 格式化为北京时间的日期字符串 (YYYY-MM-DD)
 */
export const formatBeijingDate = (date) => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-CA', { timeZone: 'Asia/Shanghai' });
};
