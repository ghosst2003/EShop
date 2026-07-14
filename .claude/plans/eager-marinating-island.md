# 面对面交易（Face-to-Face / Local Deal）功能

## Context

某些国家允许"面对面交易"——商品不走邮寄，买卖双方直接线下联系完成交易。卖家在商品页面开启此功能后，会展示联系方式和支付方式，买家线下联系卖家完成交易。类似 Facebook Marketplace 的"联系卖家"模式。

**核心特点：**
- 纯线下支付（见面付/现金/转账），不走平台支付
- 每个商品一个开关，开启后显示联系方式 + 支付方式
- 国家级别控制哪些国家允许面对面交易

---

## 数据模型改动

### 1. Product 表（`app/models/product.py`）

新增 3 个字段：
- `pickup_enabled` (Integer, default=0) — 是否允许面对面交易
- `pickup_contact` (String(200), nullable) — 联系方式（如 WhatsApp 号、电话、微信等）
- `pickup_payment` (Text, nullable) — 支付方式说明（如"现金、银行转账"等）

### 2. Country 表（`app/models/country.py`）

新增 1 个字段：
- `pickup_enabled` (Integer, default=0) — 该国家是否允许面对面交易

### 3. Order 表（`app/models/order.py`）— 暂不需要改动

面对面交易不走线上订单流程，买家看到联系方式后直接线下联系卖家完成交易。
如果后续需要记录线下订单，可再加 `fulfillment_type` 字段。

---

## 前端改动

### 4. admin — ProductForm.vue

在库存管理区域下方新增「面对面交易」配置区块：
- el-switch 开关「允许面对面交易」
- 开启后显示：
  - 联系方式输入框（String，如 WhatsApp: +49 xxx / 电话 / 微信）
  - 支付方式说明（Text，多行，如 "接受现金、银行转账"）
- 样式参考现有库存区域的 flex 布局

### 5. buyer — ShippingInfo.vue

在 Shipping/Returns/Payments 区块之后新增一行：
- 仅在商品 `pickup_enabled=true` 且买家所在国家 `pickup_enabled=true` 时显示
- 显示内容：
  ```
  当面交易:  🤝 Local deal available
  联系方式: [pickup_contact]
  支付方式: [pickup_payment]
  ```
- 样式与现有行保持一致（左侧 label，右侧内容）

### 6. buyer — ProductDetail.vue

如果 ShippingInfo 不够展示，可在商品详情页面增加一个独立的 "Local Deal" 提示卡片（放在 ShippingInfo 上方或 CTA 按钮附近），用醒目的样式展示联系方式和支付方式。

---

## API 改动

### 7. 产品公开接口

在 `products_public.py` 的产品详情返回中增加 `pickup_enabled`、`pickup_contact`、`pickup_payment` 字段（更新 `ProductOut` schema）。

### 8. 国家列表接口

在国家列表返回中增加 `pickup_enabled` 字段（更新 `CountryOut` schema）。

### 9. admin 产品 API

在 `admin_products.py` 中确保 `ProductCreate`/`ProductUpdate` schema 包含 pickup 相关字段，路由处理时自动保存。

---

## 实现步骤

### Step 1: 数据库迁移

创建 `migrate_pickup.py`：
```python
# ALTER TABLE products ADD COLUMN pickup_enabled INT DEFAULT 0
# ALTER TABLE products ADD COLUMN pickup_contact VARCHAR(200)
# ALTER TABLE products ADD COLUMN pickup_payment TEXT
# ALTER TABLE countries ADD COLUMN pickup_enabled INT DEFAULT 0
```

### Step 2: 更新 SQLAlchemy Models

- `app/models/product.py` — 新增 pickup_enabled, pickup_contact, pickup_payment
- `app/models/country.py` — 新增 pickup_enabled
- `app/models/__init__.py` — 确保导入

### Step 3: 更新 Pydantic Schemas

- `app/schemas/product.py` — ProductCreate/ProductUpdate/ProductOut 增加 3 个 pickup 字段
- 查找 Country schema 文件（可能在 `app/schemas/` 下）— 增加 pickup_enabled

### Step 4: admin — ProductForm.vue

新增面对面交易配置区块，样式与库存区域对齐。

### Step 5: admin 产品 API 确认

确认 `admin_products.py` 的 create/update 路由处理 pickup 字段（如果用了 model_dump 应该自动处理）。

### Step 6: buyer — ShippingInfo.vue

新增当面交易行，条件渲染。

### Step 7: buyer — ProductDetail.vue（可选）

如果 ShippingInfo 中展示不够醒目，在 ShippingInfo 上方增加一个独立的「🤝 当面交易可用」提示卡片，展示联系方式和支付方式。

---

## 验证

1. 运行 `python migrate_pickup.py` 确认字段添加成功
2. 在 admin 国家管理页开启某国家的 pickup_enabled（如 DE）
3. 在 admin ProductForm 创建/编辑商品，开启面对面交易，填写联系方式和支付方式
4. 在 buyer 端切换国家到已开启的国家，访问商品详情页，应能看到当面交易信息
5. 切换到未开启的国家，当面交易信息应隐藏
6. 关闭商品级别的 pickup_enabled，当面交易信息应隐藏
