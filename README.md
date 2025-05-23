# 二手书籍买卖管理系统

一个简单易用的二手书籍买卖管理网站，帮助您轻松管理书籍库存和销售。

## 功能特色

### 📚 书籍管理
- **添加书籍**：轻松添加新的二手书籍信息
- **编辑信息**：修改书籍的标题、作者、价格、状况等信息
- **删除书籍**：移除不再销售的书籍
- **状态管理**：一键标记书籍为已售出或重新上架

### 🛒 用户购买界面
- **浏览书籍**：用户可以查看所有可购买的书籍
- **详细信息**：查看书籍的详细描述、价格、状况等
- **联系购买**：提供店主联系方式，方便用户购买

### 📊 销售管理
- **统计面板**：实时显示总书籍数、可售数量、已售数量
- **销售记录**：追踪哪些书籍已经卖出，以及售出时间
- **库存管理**：清晰了解哪些书籍还在库存中

## 技术栈

- **后端**：Flask (Python)
- **数据库**：SQLite
- **前端**：Bootstrap 5 + HTML/CSS/JavaScript
- **图标**：Bootstrap Icons

## 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境（如果还没有激活）
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app.py
```

### 3. 访问网站

打开浏览器访问：`http://localhost:5000`

## 使用指南

### 首次使用

1. **启动应用**：运行 `python app.py`
2. **添加书籍**：点击导航栏的"添加书籍"开始添加您的第一本书
3. **管理书籍**：在"管理"页面查看所有书籍和统计信息

### 日常管理

#### 添加新书籍
1. 点击"添加书籍"按钮
2. 填写书籍信息（书名和作者为必填项）
3. 选择书籍状况（全新、九成新等）
4. 设置合理的价格
5. 添加书籍描述（可选）

#### 管理现有书籍
1. 在管理中心查看所有书籍
2. 使用操作按钮进行：
   - 📝 编辑书籍信息
   - ✅ 标记为售出
   - 🔄 重新上架
   - 🗑️ 删除书籍

#### 查看销售情况
- 管理中心顶部显示实时统计
- 表格中清楚标明每本书的状态
- 已售出书籍显示售出时间

### 用户购买流程

1. **浏览书籍**：用户在首页查看可购买的书籍
2. **查看详情**：点击"查看详情"了解书籍完整信息
3. **联系购买**：点击"联系购买"按钮获取店主联系方式

## 数据库结构

### Book 表
- `id`: 书籍唯一标识
- `title`: 书名
- `author`: 作者
- `isbn`: ISBN号码（可选）
- `price`: 价格
- `condition`: 书籍状况
- `description`: 描述
- `is_sold`: 是否已售出
- `date_added`: 上架时间
- `date_sold`: 售出时间

## 页面功能

### 主要页面

1. **首页** (`/`) - 显示所有可购买的书籍
2. **管理中心** (`/admin`) - 书籍管理和统计
3. **添加书籍** (`/add_book`) - 添加新书籍表单
4. **编辑书籍** (`/edit_book/<id>`) - 编辑书籍信息
5. **书籍详情** (`/book_details/<id>`) - 查看书籍完整信息

### API接口

- `GET /api/stats` - 获取统计数据（JSON格式）

## 自定义配置

### 修改联系方式
编辑 `templates/book_details.html` 文件中的 `contactSeller()` 函数，更新您的联系信息。

### 修改样式
- 主要样式在 `templates/base.html` 的 `<style>` 标签中
- 使用 Bootstrap 5 类进行快速样式调整

### 数据库配置
在 `app.py` 中修改数据库配置：
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
```

## 常见问题

### 如何备份数据？
数据存储在 `bookstore.db` 文件中，定期复制此文件即可备份。

### 如何重置数据库？
删除 `bookstore.db` 文件，重新运行应用即可创建新的空数据库。

### 如何部署到服务器？
1. 设置生产环境的数据库
2. 修改 `app.py` 中的 `debug=False`
3. 使用 Gunicorn 或其他 WSGI 服务器运行

## 开发说明

### 项目结构
```
book_manager/
├── app.py              # 主应用文件
├── requirements.txt    # 依赖列表
├── bookstore.db       # SQLite 数据库（运行后生成）
├── templates/         # HTML 模板
│   ├── base.html      # 基础模板
│   ├── index.html     # 首页
│   ├── admin.html     # 管理页面
│   ├── add_book.html  # 添加书籍
│   ├── edit_book.html # 编辑书籍
│   └── book_details.html # 书籍详情
└── README.md          # 项目说明
```

### 扩展功能建议
- 用户系统和权限管理
- 图片上传功能
- 搜索和筛选功能
- 销售报表生成
- 微信小程序接口
- 在线支付集成

## 许可证

本项目采用 MIT 许可证，可自由使用和修改。

## 联系支持

如有问题或建议，请通过以下方式联系：
- 📧 邮箱：support@bookstore.com
- 💬 微信：bookstore_support 

## 部署到Vercel

### 使用Vercel Postgres（推荐）

我们强烈推荐使用Vercel Postgres作为数据库，它提供了简单的集成和自动配置。

#### 快速部署步骤：

1. **推送代码到GitHub**
2. **在Vercel导入项目**
3. **添加Vercel Postgres存储**
4. **设置环境变量**
5. **部署完成**

> 📖 **详细指南**：请查看 [VERCEL_POSTGRES_SETUP.md](./VERCEL_POSTGRES_SETUP.md) 获取完整的部署指南。

#### 必需的环境变量：

```env
SECRET_KEY=your-super-secret-key-change-this-in-production
ADMIN_PASSWORD=your-secure-admin-password
```

**注意**：Vercel Postgres会自动提供数据库连接环境变量，无需手动配置。

### 前置准备

1. 注册Vercel账号：https://vercel.com
2. 安装Vercel CLI：`npm i -g vercel`
3. 准备数据库（推荐使用PostgreSQL）

### 部署步骤

1. **Fork或下载项目到你的GitHub仓库**

2. **在Vercel上导入项目**
   - 登录Vercel控制台
   - 点击"New Project"
   - 从GitHub导入你的仓库

3. **配置环境变量**
   在Vercel项目设置中添加以下环境变量：
   ```
   SECRET_KEY=your-super-secret-key-change-this-in-production
   ADMIN_PASSWORD=your-secure-admin-password
   DATABASE_URL=postgresql://username:password@hostname:port/database_name
   ```

4. **数据库配置**
   - 如果使用PostgreSQL，需要先创建数据库
   - 推荐使用Vercel的PostgreSQL集成或其他云数据库服务
   - SQLite在Vercel上不持久，不适合生产环境

5. **部署**
   - Vercel会自动检测到Flask应用并进行部署
   - 首次部署时会自动创建数据库表

### 推荐的数据库选择

由于Vercel是无服务器环境，SQLite数据库在每次冷启动时会丢失数据。推荐使用以下数据库：

1. **Vercel Postgres** (强烈推荐) ⭐
2. **Supabase** (免费PostgreSQL)
3. **PlanetScale** (MySQL)
4. **Railway** (PostgreSQL/MySQL)

### 本地开发

```bash
# 克隆项目
git clone <your-repo-url>
cd book_manager

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
```

### 注意事项

- 生产环境中一定要更改默认的SECRET_KEY和ADMIN_PASSWORD
- 如果使用PostgreSQL，需要安装额外的依赖：`pip install psycopg2-binary`
- Vercel的免费计划有一些限制，请查看官方文档了解详情 