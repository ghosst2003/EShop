# ESHShop — 开发设计文档

> 欧洲二手商品商城 v1.0 | 2026-06-02

---

## 1. 项目概述

面向欧洲运营的二手商品交易平台，前后端分离架构。第一版为纯展示型商城，不接入支付。

### 端侧划分

| 端 | 用途 | 平台 | 语言 |
|----|------|------|------|
| 买家端（PC） | 浏览/搜索/查看商品 | 浏览器 1440px | 英文 |
| 买家端（手机） | 浏览/搜索/查看商品 | 手机浏览器 375px | 英文 |
| 管理端 | 上传/编辑/管理商品 | 后台 PC | 中文 |

---

## 2. 技术栈

| 层级 | 选型 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| 前端框架（管理端） | Vue 3 + Vite + Element Plus |
| 前端框架（买家端） | Vue 3 + Vite + Tailwind CSS |
| ORM | SQLAlchemy 2.0 |
| 数据库 | MySQL 8.0 (utf8mb4) |
| 认证 | JWT (HS256) + bcrypt |
| 图片处理 | Pillow (缩略图) |
| 部署 | 前端构建 → `backend/static/`，FastAPI 单进程挂载 |

---

## 3. 设计系统

### 3.1 色彩体系（淘宝橙色调）

| 色名 | 色值 | 用途 |
|------|------|------|
| 主橙 | `#FF4400` | 导航栏、价格、按钮、强调元素 |
| 浅橙白 | `#FFF5F0` | 搜索框背景、Hero 卡片背景 |
| 更浅橙 | `#FFE8DD` | 未选中分类胶囊、装饰光晕 |
| 深灰正文 | `#333333` | 正文、标题 |
| 中灰次要 | `#666666` | 副标题、辅助文字 |
| 浅灰说明 | `#999999` | 占位符、时间信息 |
| 页脚深灰 | `#1B1B1B` | Footer 背景 |
| 页脚链接 | `#888888` | Footer 链接文字 |
| 页脚底部 | `#555555` | Copyright 文字 |
| 白色 | `#FFFFFF` | 卡片背景、导航文字 |
| 图片占位 | `#EBEBF0` | 图片未加载时的占位 |
| 背景灰白 | `#F2F3F7` | 页面整体背景 |
| 绿色成色 | `#16A34A` / `#DCFCE7` | "Like New" 标签 |
| 琥珀成色 | `#D97706` / `#FEF3C7` | "Good" 标签 |
| 紫色成色 | `#7C3AED` / `#EDE9FE` | "Fair" 标签 |

### 3.2 字体体系

- **字体**: Inter（PC & Mobile）
- **字重**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold), 800 (extra-bold), 900 (black)
- **行高**: Tailwind 默认 (1.5x)

### 3.3 间距体系 (8px 基准)

| 间距 | 用途 |
|------|------|
| 4px | 徽章内边距 |
| 8px | 小组件间距 |
| 16px | 卡片内边距 |
| 24px | 区块间距 |
| 32px | 大区块间距 |
| 48px | Hero 区域间距 |

### 3.4 圆角

| 值 | 用途 |
|----|------|
| 4px | 小标签 |
| 6px | 折扣标签 |
| 8px | 图片 |
| 10px | 按钮 |
| 12px | 卡片 |
| 16px | 大卡片 |
| 20px | 导航搜索框、按钮 |
| 24px | Hero 卡片 |

---

## 4. 买家端 — PC 布局 (1440px)

### 4.1 导航栏 (72px 高)
- 左侧：Logo（橙色方块 + "ESHShop"白色文字）
- 中间：Home / Browse / Categories / About
- 右侧：搜索框（浅橙白背景）+ 用户头像
- 背景色：`#FF4400` 主橙

### 4.2 Hero 区域 (520px 高)
- 背景色：`#FF4400` 主橙
- 左侧：Badge "Sustainable Shopping" → 大标题 "Find Quality Second-Hand Goods in Europe" → 副标题 → 双按钮
- 主按钮：白色背景 + 橙色文字 "Browse Now"
- 次按钮：浅橙背景 + 白色文字 "How It Works"
- 右侧：商品展示卡片（浅橙白背景，含图片占位 + 标题 + 价格标签）
- 底部信任徽章：Buyer Protection / Secure Payment / EU-Wide / Eco-Friendly

### 4.3 分类快速导航 (120px 高)
- 白色背景
- 标题 "Browse by Category"
- 分类胶囊：Electronics（主橙高亮）/ Fashion / Home & Living / Sports / Books

### 4.4 商品网格区
- 标题 "Latest Products" + 副标题 + 右侧 "View All"（橙色）
- 4 列商品卡片 (310×420px)：
  - 白色圆角卡片
  - 图片占位 (310×250px)
  - 左上：成色标签（绿色/琥珀/紫）
  - 右上：收藏按钮 ♡
  - 商品标题 (17px 粗体)
  - 品牌信息 (灰色)
  - 价格行：橙色大字售价 + 灰色原价 + 黄色折扣百分比标签
  - 底部 "Listed X ago" (灰色小字)

### 4.5 How It Works 区域
- 白色背景
- 居中标题 "How It Works" + 副标题
- 3 步骤卡片（浅橙白背景）：
  1. Browse and Discover（深灰编号圆）
  2. Contact the Seller（深灰编号圆）
  3. Enjoy Your Find（橙色编号圆）

### 4.6 Footer
- 深灰背景 `#1B1B1B`
- 左侧：Logo + 标语
- 三栏链接：Shop / Legal / Contact
- 底部 Copyright + "Made in Europe"

### 4.7 Cookie 同意横幅
- 底部浮动白色圆角卡片
- Cookie 图标 + 文字说明
- "Accept All"（深灰按钮）+ "Customise"（浅橙白按钮）

---

## 5. 买家端 — 手机布局 (375px)

### 5.1 顶部搜索栏 (50px + 44px 状态栏)
- 背景色：`#FF4400` 主橙（延伸自 PC 导航）
- 左侧 "Scan" 快捷入口
- 居中搜索框（白色圆角）
- 右侧 "Msg" 快捷入口

### 5.2 轮播 Banner (140px 高)
- 橙色圆角卡片
- "Second-Hand Treasure Hunt" 大标题
- 副标题 + 轮播指示点

### 5.3 分类图标网格 (2行×5列)
- 大字号首字母图标（E/F/H/S/B/T/A/G/W/+）
- 每个图标用不同颜色区分
- 底部文字标签：Electronics/Fashion/Home/Sports/Books/Toys/Auto/Garden/Tools/More

### 5.4 限时抢购区
- 红色 "FLASH SALE" 标签
- 倒计时 "Ends in 02:45:30"
- 右侧 "More >"
- 横向滚动小商品卡片（70×70 图片 + 价格）

### 5.5 猜你喜欢 — 双列瀑布流
- 标题 "Guess You Like" + "Based on your browsing"
- 左右两列不等高商品卡片：
  - 全宽图片 (350×130~170px)
  - 成色标签叠加在图片左上
  - 收藏按钮叠加在图片右上
  - 商品标题 (12px 多行)
  - 橙色大字价格 "EUR 45"
  - 热度标签 "128 saved" / "256 sold"

### 5.6 底部 Tab 导航 (80px 高)
- Home（橙色高亮）/ Browse / Messages / Cart / Me
- 白色背景

### 5.7 Cookie 同意
- 底部浮动卡片 + "Accept"（橙）/ "Settings"（浅橙白）

---

## 6. 管理端布局 (PC, 中文界面)

> 待设计，参考以下页面结构：
> - 登录页
> - 商品管理（列表 + 搜索 + 状态筛选）
> - 商品表单（中/英文标题、描述、分类选择、成色、多图上传）
> - 分类管理
> - GDPR 请求处理面板

---

## 7. 数据库设计

### 7.1 核心表

```
users ──< products ──< product_images
  │         │
  │         └──< categories
  │
  └──< operation_logs
  └──< data_deletion_requests (processed_by)

gdpr_consent_logs (session 级别)
```

### 7.2 表结构

**users**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT UNSIGNED PK | 自增主键 |
| username | VARCHAR(50) UNIQUE | 登录用户名 |
| password_hash | VARCHAR(255) | bcrypt 哈希 |
| role | ENUM('admin') | v1 仅管理员 |
| display_name | VARCHAR(100) | 显示名称 |
| email | VARCHAR(255) | 邮箱 |
| is_active | TINYINT(1) | 是否启用 |
| created_at / updated_at | DATETIME | 时间戳 |

**categories**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT UNSIGNED PK | 自增主键 |
| parent_id | INT UNSIGNED FK→categories | 父分类（多级） |
| name | VARCHAR(100) | 中文名称（管理端） |
| name_en | VARCHAR(100) | 英文名称（买家端） |
| slug | VARCHAR(100) UNIQUE | URL 标识 |
| sort_order | INT UNSIGNED | 排序 |
| is_active | TINYINT(1) | 是否启用 |

**products**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT UNSIGNED PK | 自增主键 |
| category_id | INT UNSIGNED FK→categories | 分类 |
| title | VARCHAR(255) | 中文标题 |
| title_en | VARCHAR(255) | 英文标题 |
| description | TEXT | 中文描述 |
| description_en | TEXT | 英文描述 |
| original_price | DECIMAL(10,2) | 原价（可为空） |
| sale_price | DECIMAL(10,2) | 售价 |
| currency | VARCHAR(3) DEFAULT 'EUR' | 货币 |
| condition_grade | ENUM('new','like_new','good','fair','poor','for_parts') | 成色 |
| condition_note | TEXT | 成色备注 |
| brand | VARCHAR(100) | 品牌 |
| tags | JSON | 标签数组 |
| status | ENUM('draft','active','sold','archived') | 状态 |
| views_count | INT UNSIGNED | 浏览次数 |
| published_at | DATETIME | 发布时间 |
| created_by | INT UNSIGNED FK→users | 创建人 |
| created_at / updated_at | DATETIME | 时间戳 |

**product_images**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT UNSIGNED PK | 自增主键 |
| product_id | INT UNSIGNED FK→products | 所属商品 |
| image_url | VARCHAR(500) | 图片路径 |
| thumbnail_url | VARCHAR(500) | 缩略图路径 |
| alt_text | VARCHAR(255) | 替代文字 |
| sort_order | INT UNSIGNED | 排序 |
| is_primary | TINYINT(1) | 是否主图 |

**gdpr_consent_logs** — Cookie 同意审计
**data_deletion_requests** — GDPR 数据删除/导出请求
**operation_logs** — 管理端操作审计日志

---

## 8. API 端点

### 8.1 认证
| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | `/api/auth/login` | 管理员登录 | 无 |
| GET | `/api/auth/me` | 获取当前管理员信息 | 管理员 |

### 8.2 买家端（公开）
| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | `/api/products` | 商品列表（分页/筛选） | page, page_size, category_id, condition_grade, price_min/max, sort, brand, tag |
| GET | `/api/products/{id}` | 商品详情 | 无 |
| GET | `/api/categories` | 分类列表（树形） | 无 |
| POST | `/api/gdpr/consent` | 记录 Cookie 同意 | 无 |
| POST | `/api/gdpr/data-request` | 提交数据请求 | 无 |

### 8.3 管理端（需鉴权）
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/products` | 商品列表（含草稿） |
| POST | `/api/admin/products` | 创建商品 |
| GET | `/api/admin/products/{id}` | 商品详情 |
| PUT | `/api/admin/products/{id}` | 更新商品 |
| DELETE | `/api/admin/products/{id}` | 软删除 |
| PATCH | `/api/admin/products/{id}/status` | 变更状态 |
| POST | `/api/admin/products/{id}/images` | 上传图片 |
| DELETE | `/api/admin/products/{id}/images/{img_id}` | 删除图片 |
| GET/POST/PUT/DELETE | `/api/admin/categories` | 分类 CRUD |
| GET | `/api/admin/gdpr/requests` | GDPR 请求列表 |
| PATCH | `/api/admin/gdpr/requests/{id}` | 处理请求 |

---

## 9. 目录结构

```
ESHShop/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口，挂载 /admin / 静态目录
│   │   ├── config.py            # pydantic-settings 配置
│   │   ├── database.py          # SQLAlchemy 引擎/会话
│   │   ├── models.py            # ORM 模型
│   │   ├── schemas.py           # Pydantic 请求/响应
│   │   ├── auth.py              # JWT + bcrypt
│   │   ├── dependencies.py      # get_current_user / require_role
│   │   ├── routers/
│   │   │   ├── auth.py              # 认证
│   │   │   ├── products_public.py   # 买家端商品 API
│   │   │   ├── categories_public.py # 买家端分类 API
│   │   │   ├── admin_products.py    # 管理端商品 CRUD
│   │   │   ├── admin_categories.py  # 管理端分类 CRUD
│   │   │   ├── gdpr_public.py       # GDPR 公开接口
│   │   │   └── admin_gdpr.py        # GDPR 管理接口
│   │   ├── services/
│   │   │   ├── product_service.py
│   │   │   └── gdpr_service.py
│   │   └── utils/
│   │       └── upload.py        # 图片上传 + 缩略图
│   ├── uploads/                 # 商品图片存储
│   ├── static/
│   │   ├── admin/               # 管理端构建产物
│   │   └── buyer/               # 买家端构建产物
│   ├── schema.sql               # 数据库 DDL
│   ├── create_admin.py          # 管理员种子脚本
│   └── requirements.txt
├── frontend-admin/              # 管理端 (Vue 3 + Element Plus, 中文)
│   └── src/
│       ├── views/
│       │   ├── Login.vue
│       │   ├── Layout.vue
│       │   ├── ProductList.vue
│       │   ├── ProductForm.vue
│       │   ├── CategoryManagement.vue
│       │   └── GdprRequests.vue
│       └── components/
│           ├── ImageUploader.vue
│           └── ProductTable.vue
├── frontend-buyer/              # 买家端 (Vue 3 + Tailwind CSS, 英文)
│   └── src/
│       ├── views/
│       │   ├── Home.vue
│       │   ├── ProductList.vue
│       │   ├── ProductDetail.vue
│       │   ├── SearchResults.vue
│       │   ├── PrivacyPolicy.vue
│       │   ├── CookiePolicy.vue
│       │   ├── Imprint.vue
│       │   └── DataRequestForm.vue
│       └── components/
│           ├── CookieConsent.vue
│           ├── ProductCard.vue
│           ├── ImageGallery.vue
│           ├── FilterSidebar.vue
│           └── Footer.vue
└── start_server.py
```

---

## 10. GDPR 合规 v1

| 项目 | 实现 |
|------|------|
| Cookie 同意横幅 | 买家端首访弹出，区分必要/分析/营销类 Cookie |
| 隐私政策页面 | `/privacy` — GDPR Article 13 要求的完整信息 |
| 数据删除请求 | `/data-request` 表单 → 管理端处理面板 |
| 同意审计日志 | 所有同意记录存入 `gdpr_consent_logs`（session 级别） |
| Impressum | `/imprint` — 德国 Telemediengesetz 要求的商家信息 |
| IP 脱敏 | 日志中 IP 地址哈希化 |
| 30 天响应 | 管理端标记处理状态，追踪 GDPR 请求处理期限 |

---

## 11. 实施阶段

| 阶段 | 内容 | 预估文件数 |
|------|------|-----------|
| Phase 1 | 后端基础：schema.sql, models, config, database, auth, dependencies, main | 8 |
| Phase 2 | 后端 API：认证 + 买家端公开 API + 管理端商品/分类 CRUD + GDPR | 7 |
| Phase 3 | 后端工具：upload.py, services, create_admin.py | 4 |
| Phase 4 | 管理端前端：Vue 3 + Element Plus 初始化 + 6 页面 + 组件 | ~15 |
| Phase 5 | 买家端前端：Vue 3 + Tailwind 初始化 + 8 页面 + 组件 + 响应式 | ~20 |
| Phase 6 | GDPR 合规收尾：Cookie 横幅对接、隐私政策、数据请求流程 | 3 |

---

## 12. 验证方式

1. **后端**：`pip install -r requirements.txt` → 建表 → `create_admin.py` → `start_server.py` → 访问 `/docs`
2. **管理端**：登录 → 创建分类 → 上传商品 → 验证状态流转（draft→active→sold）
3. **买家端 PC**：1440px 浏览商品列表/详情，验证橙色主题一致性
4. **买家端手机**：Chrome DevTools 375px 视口，验证淘宝风格布局
5. **语言一致性**：管理端录入中英文 → 买家端展示英文
6. **GDPR**：Cookie 横幅 → 拒绝非必要 → 不设置跟踪 Cookie；提交数据请求 → 管理端可见
