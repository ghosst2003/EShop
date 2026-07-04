# BeCool Market - MySQL 配置说明

## 1. 填写远程 MySQL 信息

编辑 `backend/.env` 文件，修改 `DATABASE_URL`：

```env
DATABASE_URL=mysql+pymysql://用户名:密码@服务器IP:3306/eshshop
```

**示例：**
```env
DATABASE_URL=mysql+pymysql://root:MyP@ssw0rd!@47.100.123.45:3306/eshshop
```

## 2. 远程 MySQL 服务器准备

在你的远程服务器上执行：

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS eshshop 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

-- 创建远程访问用户（可选，如果用 root 可跳过）
CREATE USER 'becool'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON eshshop.* TO 'becool'@'%';
FLUSH PRIVILEGES;
```

**确保 MySQL 允许远程连接：**
```bash
# 检查 bind-address（MySQL 8.0+ 默认允许远程）
sudo grep bind-address /etc/mysql/mysql.conf.d/mysqld.cnf
# 如果是 127.0.0.1，改为 0.0.0.0 后重启 MySQL
```

## 3. 初始化数据库

```bash
cd backend
python init_db.py
```

## 4. 启动服务

```bash
# 后端
cd backend && uvicorn app.main:app --reload --port 8000

# 前台（另一个终端）
cd frontend-buyer && npm run dev

# 后台管理（另一个终端）
cd frontend-admin && npm run dev
```

## 连接信息格式

| 部分 | 说明 |
|------|------|
| `mysql+pymysql://` | 固定前缀 |
| `用户名` | MySQL 用户名 |
| `密码` | MySQL 密码（特殊字符需要 URL 编码） |
| `服务器IP` | 远程服务器 IP 或域名 |
| `3306` | MySQL 端口（默认） |
| `eshshop` | 数据库名 |
