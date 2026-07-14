# ESHShop Ubuntu 部署文档

## 项目架构

- **Backend**: FastAPI + uvicorn + MySQL
- **Frontend-buyer**: Vue 3 + Vite → build 输出到 `backend/static/buyer`
- **Frontend-admin**: Vue 3 + Vite (base: `/admin/`) → build 输出到 `backend/static/admin`
- **部署模式**: FastAPI 同时 serve API 和两个前端静态资源，单个 uvicorn 进程

## 1. 服务器环境准备

```bash
# 安装 Python 3.10+ 和 pip
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 安装 Node.js 20（用于构建前端）
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 安装 Nginx（反向代理）
sudo apt install -y nginx
```

## 2. 上传代码

```bash
# 方式一：rsync（从 Mac 推送）
rsync -avz --exclude 'node_modules' --exclude '.git' --exclude '.claude' --exclude '*.pen*' --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' --exclude '.DS_Store' /Users/yhait/works/ESHShop/ your-server:/home/ubuntu/ESHShop/

# 方式二：git clone
cd /home/ubuntu
git clone <your-repo> ESHShop
```

## 3. 构建前端

```bash
cd /home/ubuntu/ESHShop

# 买家前端
cd frontend-buyer
npm install
npm run build   # 输出到 ../backend/static/buyer
cd ..

# 管理前端
cd frontend-admin
npm install
npm run build   # 输出到 ../backend/static/admin
cd ..
```

## 4. 配置环境变量

编辑 `backend/.env`：

```env
DATABASE_URL=mysql+pymysql://root:你的密码@localhost:3306/eshshop
SECRET_KEY=生成一个随机字符串
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

> 如果数据库在同一台服务器，用 `localhost`；如果数据库在另一台服务器，用对应 IP。

## 5. 安装 Python 依赖并初始化数据库

```bash
cd /home/ubuntu/ESHShop/backend

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 初始化数据库（首次部署）
python init_db.py
```

## 6. 用 systemd 部署后端服务

```bash
sudo tee /etc/systemd/system/eshshop.service << 'EOF'
[Unit]
Description=ESHShop Backend
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/ESHShop/backend
ExecStart=/home/ubuntu/ESHShop/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable eshshop
sudo systemctl start eshshop
sudo systemctl status eshshop
```

## 7. 配置 Nginx 反向代理

```bash
sudo tee /etc/nginx/sites-available/eshshop << 'EOF'
server {
    listen 80;
    server_name your-domain.com;  # 改成你的域名或服务器 IP

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/eshshop /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

## 8. HTTPS（可选，使用 Let's Encrypt）

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 常用操作

### 前端代码更新

```bash
cd /home/ubuntu/ESHShop/frontend-buyer && npm run build
cd ../frontend-admin && npm run build
# FastAPI 自动加载新静态文件，无需重启服务
```

### 后端代码更新

```bash
cd /home/ubuntu/ESHShop
git pull          # 或上传新代码
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart eshshop
```

### 查看日志

```bash
# 后端日志
journalctl -u eshshop -f

# Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 停止/重启服务

```bash
sudo systemctl stop eshshop
sudo systemctl start eshshop
sudo systemctl restart eshshop
```

## 注意事项

1. 首次部署后，通过 `python create_admin.py` 创建管理员账号
2. 确保 `uploads` 目录有写入权限：`chmod -R 755 /home/ubuntu/ESHShop/backend/uploads`
3. 生产环境记得将 `.env` 中的 `SECRET_KEY` 改为随机字符串
4. CORS 在 `main.py` 中默认允许所有来源，生产环境可限制为实际域名
