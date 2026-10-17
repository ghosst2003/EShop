# ESHShop 部署指南

适用于 Ubuntu 22.04/24.04。默认部署目录为 `/opt/eshshop/app`，Nginx 对外提供网站，FastAPI 只监听 `127.0.0.1:8000`。

## 1. 自动部署

先解析域名到服务器公网 IP，然后获取代码：

```bash
git clone https://github.com/ghosst2003/EShop.git ~/ESHShop-deploy
cd ~/ESHShop-deploy
```

### 已有数据库和数据

使用 `--existing-db`。脚本不会安装 MySQL Server、创建数据库或修改数据库账号；它会在迁移前备份现有数据。

```bash
sudo bash deploy/deploy.sh install \
  --domain shop.example.com \
  --existing-db \
  --tls-email admin@example.com
```

首次运行会生成 `/opt/eshshop/app/backend/.env` 后暂停。编辑配置：

```bash
sudo nano /opt/eshshop/app/backend/.env
```

确认 `DATABASE_URL` 指向现有数据库，再重新运行：

```bash
sudo bash /opt/eshshop/app/deploy/deploy.sh install \
  --domain shop.example.com \
  --existing-db \
  --tls-email admin@example.com
```

备份保存在 `/var/backups/eshshop`。备份失败时脚本会停止，不会继续迁移。

如果 Python、Node.js、Nginx 和 MySQL 客户端也已安装，可增加 `--skip-packages`。云数据库使用 `--external-db`。

### 新服务器和新数据库

省略 `--existing-db`，脚本会安装并配置本机 MySQL：

```bash
sudo bash deploy/deploy.sh install \
  --domain shop.example.com \
  --www-domain www.shop.example.com \
  --tls-email admin@example.com
```

同样先编辑脚本生成的 `.env`，再重复执行安装命令。

如果已经准备好生产环境文件，可以一次完成：

```bash
sudo bash deploy/deploy.sh install \
  --domain shop.example.com \
  --existing-db \
  --env-file /root/eshshop.production.env \
  --tls-email admin@example.com
```

脚本会自动完成依赖安装、三个前端构建、数据库迁移、Nginx、systemd、HTTPS 和健康检查。

## 2. 生产环境变量

至少确认以下配置：

```env
DATABASE_URL=mysql+pymysql://eshshop:URL编码后的密码@127.0.0.1:3306/eshshop?charset=utf8mb4
SECRET_KEY=至少32位随机字符串
ENVIRONMENT=production
FRONTEND_URL=https://shop.example.com
CORS_ORIGINS=https://shop.example.com

STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
SMTP_USE_TLS=true
```

生成 `SECRET_KEY`：

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

数据库密码含 `@`、`#`、`/`、`:` 等字符时，需要先进行 URL 编码。保护配置文件：

```bash
sudo chown eshshop:eshshop /opt/eshshop/app/backend/.env
sudo chmod 600 /opt/eshshop/app/backend/.env
```

### 暂时不使用 Stripe

Stripe 两项可以留空。此时只上架“当面交易”商品；在线支付、Stripe 退款和 Webhook 暂不可用。

### 暂时不使用 SMTP

SMTP 可以留空，不影响部署和订单创建，但生产环境的新用户注册、邮箱验证和找回密码不可用。已有已验证用户和管理员仍可登录。

后续配置 Stripe 或 SMTP 后，如果使用 systemd，执行：

```bash
sudo systemctl restart eshshop
```

如果是手工启动，按 `Ctrl+C` 停止后重新执行第 4 节的启动命令。

## 3. 创建管理员

不要在生产环境运行 `init_db.py`。使用安全的交互式脚本：

```bash
cd /opt/eshshop/app/backend
sudo -u eshshop ./venv/bin/python create_admin.py \
  --username owner \
  --email owner@example.com
```

脚本会隐藏密码输入，并要求至少 12 位。

## 4. 手工启动 Python 后台

如果暂时不用 systemd，先停用服务：

```bash
sudo systemctl disable --now eshshop 2>/dev/null || true
```

在当前终端启动：

```bash
cd /opt/eshshop/app/backend

sudo -u eshshop ./venv/bin/dotenv -f .env run -- \
  ./venv/bin/uvicorn app.main:app \
  --host 127.0.0.1 \
  --port 8000 \
  --workers 1 \
  --proxy-headers \
  --forwarded-allow-ips=127.0.0.1
```

按 `Ctrl+C` 停止。检查状态：

```bash
curl http://127.0.0.1:8000/api/health
```

退出 SSH 后仍要运行，可使用 `tmux`：

```bash
sudo apt install -y tmux
tmux new -s eshshop
```

在 tmux 中执行启动命令。按 `Ctrl+B`，再按 `D` 退出；重新进入：

```bash
tmux attach -t eshshop
```

保持 `--workers 1`，否则库存预约清理任务会重复运行。

## 5. Stripe 后续接入

Webhook 地址：

```text
https://shop.example.com/api/payments/webhook
```

订阅以下事件：

- `checkout.session.completed`
- `checkout.session.expired`
- `checkout.session.async_payment_failed`
- `payment_intent.payment_failed`

先使用 `sk_test_...` 测试，完成支付和库存回滚验证后再换成正式密钥。测试与正式环境的 `whsec_...` 不能混用。

## 6. 更新、备份和状态

```bash
# 自动备份、拉取 main、构建、迁移、重启和健康检查
sudo bash /opt/eshshop/app/deploy/deploy.sh update

# 单独备份数据库和上传文件
sudo bash /opt/eshshop/app/deploy/deploy.sh backup

# 查看服务和当前提交
sudo bash /opt/eshshop/app/deploy/deploy.sh status
```

`update` 默认会重新启用 systemd。如果仍要手工启动，更新完成后执行：

```bash
sudo systemctl disable --now eshshop 2>/dev/null || true
```

然后重新执行第 4 节的启动命令。

## 7. 验收

```bash
curl -fsS https://shop.example.com/api/health
curl -I https://shop.example.com/
curl -I https://shop.example.com/mobile/
curl -I https://shop.example.com/admin/
```

再检查登录、商品浏览、购物车、当面交易下单、后台商品管理、订单管理和图片上传。配置 Stripe/SMTP 后，再测试在线支付、注册和找回密码。

## 8. 常用排错

```bash
sudo journalctl -u eshshop -f
sudo tail -f /var/log/nginx/error.log
sudo ss -lntp
```

- **502**：确认 Python 后台正在监听 `127.0.0.1:8000`。
- **数据库失败**：检查 `DATABASE_URL`、密码 URL 编码和数据库权限。
- **图片上传失败**：检查 `backend/uploads` 所有者是否为 `eshshop`。
- **注册返回 503**：检查 SMTP；未配置 SMTP 时属于预期行为。
- **Stripe 不可用**：检查两个 Stripe 环境变量和 Webhook 投递记录。

## 9. 重要路径

| 内容 | 路径 |
| --- | --- |
| 项目 | `/opt/eshshop/app` |
| 环境变量 | `/opt/eshshop/app/backend/.env` |
| 上传文件 | `/opt/eshshop/app/backend/uploads` |
| 备份 | `/var/backups/eshshop` |
| systemd | `/etc/systemd/system/eshshop.service` |
| Nginx | `/etc/nginx/sites-available/eshshop` |
