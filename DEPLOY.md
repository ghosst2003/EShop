# ESHShop 生产部署指南

本文以一台 Ubuntu 22.04/24.04 服务器为例，将 ESHShop 部署到 `https://shop.example.com`。请把文中的域名、邮箱和密码替换成自己的值。

## 0. 推荐：使用自动部署脚本

仓库提供了 [`deploy/deploy.sh`](deploy/deploy.sh)，支持首次安装、更新、备份和状态检查。脚本会安装系统依赖、创建应用用户、拉取 `main`、连接数据库、运行迁移、构建三个前端、配置 systemd/Nginx、申请 HTTPS 证书并执行健康检查。

先在服务器获取仓库并运行首次安装：

```bash
git clone https://github.com/ghosst2003/EShop.git ~/ESHShop-deploy
cd ~/ESHShop-deploy

sudo bash deploy/deploy.sh install \
  --domain shop.example.com \
  --www-domain www.shop.example.com \
  --tls-email admin@example.com
```

首次未提供 `--env-file` 时，脚本会生成 `/opt/eshshop/app/backend/.env` 并安全退出。`DATABASE_URL` 必须填写；SMTP 和 Stripe 可以暂时留空：

```bash
sudo nano /opt/eshshop/app/backend/.env
```

然后用已经安装到目标目录的脚本再次执行同一条安装命令：

```bash
sudo bash /opt/eshshop/app/deploy/deploy.sh install \
  --domain shop.example.com \
  --www-domain www.shop.example.com \
  --tls-email admin@example.com
```

如果已经准备好完整的生产配置，可以一次完成：

```bash
sudo bash deploy/deploy.sh install \
  --domain shop.example.com \
  --www-domain www.shop.example.com \
  --env-file /root/eshshop.production.env \
  --tls-email admin@example.com
```

### 使用已经存在且有数据的数据库

增加 `--existing-db` 后，脚本不会安装 MySQL Server，不会创建或删除数据库，也不会创建或修改数据库账号。它会使用 `.env` 中的 `DATABASE_URL` 先完整备份现有数据，然后才执行兼容迁移：

```bash
sudo bash /opt/eshshop/app/deploy/deploy.sh install \
  --domain shop.example.com \
  --existing-db \
  --tls-email admin@example.com
```

迁移会保留订单、商品、用户和配置数据，但可能为新功能增加字段或表。备份默认保存在 `/var/backups/eshshop`。数据库在云服务或另一台服务器时也可以使用 `--external-db`；它同样会在迁移前备份。

`--existing-db` 仍会安装应用需要的系统软件和 MySQL 客户端，但不会安装 MySQL Server。如果服务器上的 Python、Node.js、Nginx 和 MySQL 客户端也都已经准备好，可以同时增加 `--skip-packages`，完全跳过 `apt` 和 Node.js 安装步骤。

### 暂时不配置 Stripe 或 SMTP

两个服务都不会阻止脚本完成部署，可以在 `.env` 中暂时留空：

```env
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

SMTP_HOST=
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
```

- 未配置 Stripe 时，只使用当面交易商品。在线支付、Stripe 退款和 Stripe Webhook 暂不可用。
- SMTP 缺失或连接配置错误时，生产环境的新用户注册、邮箱验证和找回密码不可用。已有已验证用户和管理员仍可登录；订单邮件发送失败不会中断订单流程。
- SMTP 或 Stripe 配置完成后，编辑 `/opt/eshshop/app/backend/.env` 并执行 `sudo systemctl restart eshshop` 即可，不必重新部署。

只有确认服务器使用标准 OpenSSH 防火墙配置时，才增加 `--enable-firewall`。

后续发布、备份和检查：

```bash
sudo bash /opt/eshshop/app/deploy/deploy.sh update
sudo bash /opt/eshshop/app/deploy/deploy.sh backup
sudo bash /opt/eshshop/app/deploy/deploy.sh status
```

`update` 会先备份数据库和上传文件，再快进拉取 `origin/main`、安装依赖、构建、迁移、重启并检查 `/api/health`。下面各节保留了脚本所执行的完整手动步骤，便于排错和定制。

## 1. 部署结构

- Nginx 对外监听 80/443，并把请求转发到 FastAPI。
- FastAPI 仅监听 `127.0.0.1:8000`，同时提供 API、买家端、手机端和管理后台。
- 买家端构建到 `backend/static/buyer`。
- 手机端构建到 `backend/static/mobile`，手机浏览器会自动进入 `/mobile/`。
- 管理端构建到 `backend/static/admin`，入口为 `/admin/`。
- MySQL 只允许本机或受信任的私有网络访问。
- 当前应用包含进程内库存预约清理任务，因此生产环境使用 **1 个 uvicorn worker**。不要直接增加 worker 数量。

轻量使用建议从 2 核 CPU、2 GB 内存、20 GB SSD 起步。图片较多时应单独规划磁盘和备份空间。

## 2. 上线前准备

准备以下内容：

- 一台有公网 IP 的 Ubuntu 服务器；
- 一个域名，并把 `shop.example.com` 和 `www.shop.example.com` 的 A 记录指向服务器公网 IPv4；如果不使用 `www`，删除后续配置中的 `www` 域名；
- GitHub 仓库读取权限；
- MySQL；
- 用于注册、找回密码和订单邮件的 SMTP 账号（暂时不开放注册时可后配）；
- Stripe 账号（只做当面交易时可后配；接入时先使用测试密钥）。

生产环境注册流程依赖 SMTP。`ENVIRONMENT=production` 时未配置 SMTP，注册和密码邮件接口会返回 503。

## 3. 安装系统依赖

```bash
sudo apt update
sudo apt install -y \
  git nginx mysql-server \
  python3 python3-pip python3-venv \
  build-essential pkg-config libjpeg-dev zlib1g-dev
```

安装 Node.js 20 或更高版本（下面固定使用 Node.js 22 LTS），然后确认版本：

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x -o /tmp/nodesource_setup.sh
sudo -E bash /tmp/nodesource_setup.sh
sudo apt install -y nodejs

node --version
npm --version
python3 --version
```

Node.js 只在构建三个前端时需要，运行 FastAPI 服务时不需要。

## 4. 创建应用用户并拉取代码

```bash
sudo useradd --system \
  --create-home \
  --home-dir /opt/eshshop \
  --shell /usr/sbin/nologin \
  eshshop

sudo git clone https://github.com/ghosst2003/EShop.git /opt/eshshop/app
sudo chown -R eshshop:eshshop /opt/eshshop
```

如果仓库是私有仓库，请使用只读 Deploy Key 或 GitHub App，不要把个人访问令牌写进命令或配置文件。

## 5. 创建 MySQL 数据库

进入 MySQL：

```bash
sudo mysql
```

执行以下 SQL，并替换数据库密码：

```sql
CREATE DATABASE eshshop
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'eshshop'@'localhost'
  IDENTIFIED BY '替换成高强度数据库密码';

GRANT ALL PRIVILEGES ON eshshop.* TO 'eshshop'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

不要向公网开放 3306。如果使用云数据库，只允许应用服务器的私网地址访问，并启用数据库提供商的 TLS 连接。

数据库密码含有 `@`、`#`、`/`、`:` 等字符时，必须先对密码进行 URL 编码，再写入 `DATABASE_URL`。

## 6. 配置生产环境变量

生成应用密钥：

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

复制模板：

```bash
sudo -u eshshop cp /opt/eshshop/app/backend/.env.example /opt/eshshop/app/backend/.env
sudo -u eshshop nano /opt/eshshop/app/backend/.env
```

使用下面的生产配置作为基准：

```env
DATABASE_URL=mysql+pymysql://eshshop:URL编码后的数据库密码@127.0.0.1:3306/eshshop?charset=utf8mb4
SECRET_KEY=上一步生成的随机密钥
ACCESS_TOKEN_EXPIRE_MINUTES=480
ENVIRONMENT=production

FRONTEND_URL=https://shop.example.com
CORS_ORIGINS=https://shop.example.com,https://www.shop.example.com

# Stripe 首次联调先填 sk_test_，正式上线后再换成 sk_live_
STRIPE_SECRET_KEY=sk_test_xxx
# 第 12 节创建 Webhook 后再填写
STRIPE_WEBHOOK_SECRET=whsec_xxx

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=mailer@example.com
SMTP_PASSWORD=SMTP专用密码
SMTP_FROM_EMAIL=mailer@example.com
SMTP_USE_TLS=true

STOCK_RESERVATION_MINUTES=30
PICKUP_RESERVATION_HOURS=48
PRICES_INCLUDE_TAX=true
DEFAULT_TAX_RATE=0.19
TAX_RATES=CY:0.19,DE:0.19,FR:0.20,IT:0.22,ES:0.21,GR:0.24,NL:0.21,BE:0.21,AT:0.20,PT:0.23,IE:0.23,LU:0.17,MT:0.18
```

保护配置文件：

```bash
sudo chown eshshop:eshshop /opt/eshshop/app/backend/.env
sudo chmod 600 /opt/eshshop/app/backend/.env
```

`.env` 不应提交到 Git，也不要通过聊天或工单发送正式密钥。

## 7. 安装后端依赖

```bash
sudo -u eshshop python3 -m venv /opt/eshshop/app/backend/venv
sudo -u eshshop /opt/eshshop/app/backend/venv/bin/pip install --upgrade pip
sudo -u eshshop /opt/eshshop/app/backend/venv/bin/pip install \
  -r /opt/eshshop/app/backend/requirements.txt
```

## 8. 初始化数据库和管理员

不要在生产环境运行 `init_db.py`，它会创建固定的默认账号和密码。

首次部署时运行安全的管理员创建脚本。省略 `--password` 后脚本会隐藏输入，并要求输入两次：

```bash
cd /opt/eshshop/app/backend
sudo -u eshshop ./venv/bin/python create_admin.py \
  --username owner \
  --display-name "Store Owner" \
  --email owner@example.com
```

创建基础表后，运行当前仓库中的幂等迁移脚本：

```bash
cd /opt/eshshop/app/backend
sudo -u eshshop ./venv/bin/python migrate_db.py
sudo -u eshshop ./venv/bin/python migrate_pickup.py
sudo -u eshshop ./venv/bin/python migrate_shipping.py
sudo -u eshshop ./venv/bin/python migrate_transaction_modes.py
```

## 9. 构建全部前端

构建产物不会提交到 Git，首次部署和前端更新后都必须在服务器重新构建：

```bash
cd /opt/eshshop/app/frontend-buyer
sudo -u eshshop npm ci
sudo -u eshshop npm run build

cd /opt/eshshop/app/frontend-admin
sudo -u eshshop npm ci
sudo -u eshshop npm run build

cd /opt/eshshop/app/frontend-mobile
sudo -u eshshop npm ci
sudo -u eshshop npm run build
```

创建并保护上传目录：

```bash
sudo install -d -o eshshop -g eshshop -m 750 /opt/eshshop/app/backend/uploads
```

## 10. 配置 systemd

创建 `/etc/systemd/system/eshshop.service`：

```ini
[Unit]
Description=ESHShop production service
Wants=network-online.target
After=network-online.target mysql.service

[Service]
Type=simple
User=eshshop
Group=eshshop
WorkingDirectory=/opt/eshshop/app/backend
EnvironmentFile=/opt/eshshop/app/backend/.env
ExecStart=/opt/eshshop/app/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 --proxy-headers --forwarded-allow-ips=127.0.0.1
Restart=always
RestartSec=5
TimeoutStopSec=30
UMask=0027
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now eshshop
sudo systemctl status eshshop --no-pager
curl -fsS http://127.0.0.1:8000/api/health
```

`EnvironmentFile` 必须保留，因为 Stripe 路由直接读取进程环境变量。

## 11. 配置 Nginx、域名和 HTTPS

创建 `/etc/nginx/sites-available/eshshop`：

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name shop.example.com www.shop.example.com;

    client_max_body_size 12m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/eshshop /etc/nginx/sites-enabled/eshshop
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

只开放 SSH、HTTP 和 HTTPS：

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

域名解析生效后安装 Certbot，并签发证书：

```bash
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/local/bin/certbot
sudo certbot --nginx \
  -d shop.example.com \
  -d www.shop.example.com
sudo certbot renew --dry-run
```

如果 `/usr/local/bin/certbot` 已存在，跳过创建软链接的命令。

## 12. 配置 Stripe Checkout 和 Webhook

先使用 Stripe 测试模式：

1. 把测试 Secret key（`sk_test_...`）写入 `.env` 的 `STRIPE_SECRET_KEY`。
2. 在 Stripe Dashboard 的 Webhooks 中新增端点：

   `https://shop.example.com/api/payments/webhook`

3. 选择发送以下事件：

   - `checkout.session.completed`
   - `checkout.session.expired`
   - `checkout.session.async_payment_failed`
   - `payment_intent.payment_failed`

4. 复制该端点的 Signing secret（`whsec_...`）到 `STRIPE_WEBHOOK_SECRET`。
5. 重启应用：

```bash
sudo systemctl restart eshshop
sudo journalctl -u eshshop -n 100 --no-pager
```

完成一次测试支付，确认：

- Stripe Dashboard 中 Webhook 返回 HTTP 200；
- 支付完成后订单状态从待支付更新为已支付；
- 支付失败或 Checkout 过期时，库存预约能被释放；
- 成功页和订单详情页均能正确显示。

测试通过后，在 Stripe 激活正式模式，创建正式 Webhook 端点，并把 `.env` 中的 `sk_test_...` 与测试 `whsec_...` 分别替换为正式模式的 `sk_live_...` 和正式端点 Signing secret。测试模式与正式模式的 Webhook secret 不能混用。

## 13. 上线验收清单

运行基础检查：

```bash
curl -fsS https://shop.example.com/api/health
curl -I https://shop.example.com/
curl -I https://shop.example.com/mobile/
curl -I https://shop.example.com/admin/
```

浏览器中逐项验收：

- 注册、登录、退出、忘记密码；
- 商品浏览、筛选、详情页、购物车；
- 在线支付商品能够进入 Stripe Checkout 并完成测试支付；
- 当面交易商品展示正确的地点、时间和联系方式，并能提交预约订单；
- 混合支付方式商品不能错误合并结算；
- 后台创建、编辑、上架、下架商品；
- 后台查看订单并修改履约状态；
- 图片上传后刷新页面仍能正常显示；
- 手机访问自动进入手机端，底部导航和结算流程可用；
- 邮件中的验证和找回密码链接使用正式 HTTPS 域名。

## 14. 备份

数据库和 `backend/uploads` 都必须备份。仅备份 Git 仓库无法恢复商品图片和订单数据。

手动备份示例：

```bash
sudo install -d -m 700 /var/backups/eshshop

sudo sh -c 'mysqldump \
  --single-transaction \
  --routines \
  --triggers \
  eshshop | gzip > "/var/backups/eshshop/db-$(date +%F-%H%M).sql.gz"'

sudo tar -czf /var/backups/eshshop/uploads-$(date +%F-%H%M).tar.gz \
  -C /opt/eshshop/app/backend uploads
```

至少每天自动备份一次，并把备份复制到另一台服务器或对象存储。定期执行一次恢复演练，确认备份文件确实可用。

## 15. 日常更新

每次更新前先备份数据库和上传目录。然后执行：

```bash
cd /opt/eshshop/app
sudo -u eshshop git pull --ff-only origin main

sudo -u eshshop ./backend/venv/bin/pip install -r backend/requirements.txt

cd /opt/eshshop/app/frontend-buyer
sudo -u eshshop npm ci
sudo -u eshshop npm run build

cd /opt/eshshop/app/frontend-admin
sudo -u eshshop npm ci
sudo -u eshshop npm run build

cd /opt/eshshop/app/frontend-mobile
sudo -u eshshop npm ci
sudo -u eshshop npm run build

cd /opt/eshshop/app/backend
sudo -u eshshop ./venv/bin/python migrate_db.py
sudo -u eshshop ./venv/bin/python migrate_pickup.py
sudo -u eshshop ./venv/bin/python migrate_shipping.py
sudo -u eshshop ./venv/bin/python migrate_transaction_modes.py

sudo systemctl restart eshshop
curl -fsS https://shop.example.com/api/health
```

## 16. 日志与排错

```bash
# 应用实时日志
sudo journalctl -u eshshop -f

# 本次启动日志
sudo journalctl -u eshshop -b --no-pager

# Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 检查服务和监听端口
sudo systemctl status eshshop nginx mysql --no-pager
sudo ss -lntp
```

常见问题：

- **502 Bad Gateway**：先检查 `systemctl status eshshop`，再检查 8000 是否仅监听在 `127.0.0.1`。
- **静态页面 404**：确认三个前端都执行过 `npm run build`。
- **Stripe 回调失败**：检查公网 HTTPS、Webhook URL、事件列表、`STRIPE_WEBHOOK_SECRET` 和应用日志。
- **注册返回 503**：检查 SMTP 配置和 SMTP 服务商是否允许当前服务器发送邮件。
- **图片上传失败**：检查 Nginx 的 `client_max_body_size` 和 `backend/uploads` 的所有者。
- **数据库连接失败**：检查 `DATABASE_URL`、密码 URL 编码、MySQL 用户权限和 MySQL 服务状态。

## 17. 回滚原则

代码更新前记录当前版本：

```bash
cd /opt/eshshop/app
git rev-parse HEAD
```

需要回滚时，检出上一个已验证的提交，重新安装依赖、构建三个前端并重启服务。数据库回滚应使用更新前备份；不要在未备份时直接删除表或字段。

## 官方参考

- [Stripe Webhooks](https://docs.stripe.com/webhooks)
- [Stripe API keys](https://docs.stripe.com/keys)
- [Stripe Checkout fulfillment](https://docs.stripe.com/checkout/fulfillment)
- [Certbot with Nginx on Ubuntu](https://certbot.eff.org/instructions?ws=nginx&os=snap)
