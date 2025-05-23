# Vercel Postgres 部署指南

本指南将帮助你使用Vercel Postgres作为数据库部署Flask书店管理系统。

## 📋 前置条件

1. ✅ Vercel账号（免费版即可）
2. ✅ GitHub仓库（包含本项目代码）
3. ✅ 项目已配置好Vercel部署文件

## 🚀 部署步骤

### 步骤1：将代码推送到GitHub

```bash
# 确保所有文件已提交
git add .
git commit -m "配置Vercel Postgres部署"
git push origin main
```

### 步骤2：在Vercel上创建项目

1. 访问 [Vercel控制台](https://vercel.com/dashboard)
2. 点击 **"New Project"**
3. 选择你的GitHub仓库
4. 点击 **"Import"**

### 步骤3：添加Vercel Postgres存储

1. 在项目页面，点击 **"Storage"** 标签
2. 点击 **"Create Database"**
3. 选择 **"Postgres"**
4. 输入数据库名称（例如：`bookstore-db`）
5. 选择区域（推荐选择离你用户最近的区域）
6. 点击 **"Create"**

### 步骤4：配置环境变量

Vercel会自动为你的项目添加以下环境变量：
- `POSTGRES_URL`
- `POSTGRES_PRISMA_URL`
- `POSTGRES_URL_NON_POOLING`
- `POSTGRES_USER`
- `POSTGRES_HOST`
- `POSTGRES_PASSWORD`
- `POSTGRES_DATABASE`

你只需要手动添加应用特定的环境变量：

1. 在项目设置页面，找到 **"Environment Variables"**
2. 添加以下变量：

```
SECRET_KEY=your-super-secret-key-change-this-in-production
ADMIN_PASSWORD=your-secure-admin-password
```

### 步骤5：重新部署

1. 回到项目的 **"Deployments"** 页面
2. 点击最新部署右侧的 **"..."** 菜单
3. 选择 **"Redeploy"**

## 🎯 部署后验证

### 检查数据库连接

1. 访问你的Vercel应用URL
2. 如果首页能正常显示，说明数据库连接成功
3. 数据库表会在首次访问时自动创建

### 测试管理功能

1. 访问 `your-app-url/admin_login`
2. 使用你设置的 `ADMIN_PASSWORD` 登录
3. 尝试添加一本测试书籍

### 查看日志

如果遇到问题，可以在Vercel控制台的 **"Functions"** 页面查看实时日志。

## 🔧 常见问题解决

### 问题1：连接超时

如果遇到数据库连接超时，检查：
- Vercel Postgres是否已正确创建
- 环境变量是否已正确设置
- 重新部署项目

### 问题2：SSL连接错误

我们的配置已经包含了SSL设置，如果仍有问题，检查：
- 是否使用了正确的 `POSTGRES_URL`
- Vercel Postgres实例是否启用了SSL

### 问题3：表未创建

如果数据库表没有自动创建：
1. 检查应用日志
2. 手动运行数据库初始化（见下方）

## 🛠️ 手动数据库初始化

如果需要手动初始化数据库，可以使用Vercel CLI：

```bash
# 安装Vercel CLI
npm i -g vercel

# 登录Vercel
vercel login

# 在项目目录中链接项目
vercel link

# 运行数据库初始化脚本
vercel env pull .env.local
python init_db.py
```

## 💡 性能优化建议

1. **连接池设置**：我们已经配置了连接池，无需额外设置
2. **索引优化**：如果数据量大，考虑为常查询字段添加索引
3. **查询优化**：使用SQLAlchemy的延迟加载优化查询性能

## 📊 监控和维护

### 数据库使用情况

在Vercel控制台的Storage页面可以查看：
- 数据库大小
- 连接数
- 查询性能统计

### 备份策略

Vercel Postgres提供自动备份功能，但建议：
- 定期导出重要数据
- 测试恢复流程

## 🔐 安全最佳实践

1. **强密码**：使用强密码作为管理员密码
2. **密钥轮换**：定期更换 `SECRET_KEY`
3. **访问控制**：只为需要的人员提供Vercel项目访问权限
4. **监控日志**：定期检查应用访问日志

## 📈 扩展功能

一旦基本部署完成，你可以考虑添加：
- 用户注册和登录系统
- 图片上传（使用Vercel Blob）
- 邮件通知（使用第三方邮件服务）
- 支付集成
- API接口

## 🆘 获取帮助

如果遇到问题：
1. 查看 [Vercel文档](https://vercel.com/docs)
2. 检查 [Vercel社区](https://github.com/vercel/vercel/discussions)
3. 查看应用日志找到具体错误信息

---

🎉 恭喜！你的Flask书店管理系统现在已经部署在Vercel上，使用Vercel Postgres作为数据库！ 