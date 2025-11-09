# 登录认证配置说明

DeskMemo 支持可选的密码保护功能，通过环境变量配置。

## 配置方法

### 1. 编辑后端配置文件

编辑 `backend/.env` 文件（如果不存在，复制 `backend/.env.example`）：

```bash
# Authentication
# 前端登录密码（留空则不启用登录验证）
AUTH_PASSWORD=your_secure_password_here
```

### 2. 配置选项

**启用密码保护：**
```bash
AUTH_PASSWORD=mySecurePassword123
```

**禁用密码保护（默认）：**
```bash
AUTH_PASSWORD=
```
或者完全删除这一行。

## 功能特性

### 启用认证后
- 访问前端任何页面都需要先登录
- 后端所有 API 接口（除登录接口外）都需要 token 验证
- Token 存储在浏览器 localStorage 中
- 支持登出功能，清除 token

### 未启用认证时
- 无需登录即可访问所有页面
- API 请求不需要 token
- 导航栏不显示登出按钮

## 安全建议

1. **生产环境务必设置密码**
   ```bash
   AUTH_PASSWORD=使用强密码，包含大小写字母、数字和特殊字符
   ```

2. **定期更换密码**
   - 修改 `.env` 文件中的密码
   - 重启后端服务
   - 所有用户需要重新登录

3. **使用 HTTPS**
   - 生产环境建议使用反向代理（如 Nginx）配置 HTTPS
   - 防止密码在传输过程中被窃取

4. **保护配置文件**
   ```bash
   chmod 600 backend/.env  # 限制文件访问权限
   ```

## 使用流程

### 首次访问
1. 用户访问前端 URL（如 `http://localhost:3000`）
2. 系统检测是否启用认证
3. 如果启用，自动跳转到登录页面
4. 输入配置的密码
5. 登录成功后跳转到首页

### 登出
- 点击导航栏右上角的"登出"按钮
- Token 被清除
- 自动跳转到登录页面

### Token 失效
- 如果后端重启，所有 token 失效
- 用户需要重新登录
- 系统会自动检测并跳转到登录页面

## 技术实现

### 后端
- 简单的密码验证（直接比对）
- 生成随机 token（使用 `secrets.token_urlsafe`）
- Token 存储在内存中（重启后失效）
- 使用 FastAPI Depends 机制进行路由保护

### 前端
- React Router 路由守卫
- Axios 拦截器自动添加 token
- 401 错误自动跳转登录页
- localStorage 持久化 token

## 故障排查

### 无法登录
1. 检查 `backend/.env` 文件中的密码配置
2. 确认后端服务已重启
3. 查看浏览器控制台错误信息
4. 检查后端日志

### 频繁要求登录
1. 检查后端服务是否频繁重启
2. 查看浏览器 localStorage 是否被清除
3. 确认浏览器支持 localStorage

### 密码忘记
- 修改 `backend/.env` 文件中的 `AUTH_PASSWORD`
- 重启后端服务
- 使用新密码登录

## 示例配置

### 开发环境（本地测试）
```bash
# 不启用认证，方便开发
AUTH_PASSWORD=
```

### 生产环境
```bash
# 启用强密码保护
AUTH_PASSWORD=Td$9mK#pL2nX@vQ8wZ
```

## 升级说明

从未启用认证的旧版本升级：
1. 更新代码到最新版本
2. 在 `backend/.env` 中添加 `AUTH_PASSWORD` 配置
3. 重启后端服务
4. 前端无需修改，自动适配

## 未来改进方向

当前实现为简单的单密码验证，适合个人使用。未来可考虑：
- 多用户支持
- 用户名+密码验证
- JWT token 认证
- Session 持久化（Redis）
- 密码加密存储
- 登录日志记录
- IP 白名单
