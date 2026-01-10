# VPS 部署指南

本指南将帮助你在 CentOS/Ubuntu VPS 上部署此导航网站。

## 1. 环境准备

确保你的 VPS 已安装 Python 3 和 MySQL。

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv mysql-server libmysqlclient-dev
```

### CentOS/RHEL
```bash
sudo yum install python3 python3-pip mysql-server python3-devel mysql-devel
```

## 2. 数据库配置

登录 MySQL 并创建数据库：

```bash
sudo mysql -u root -p
```

在 MySQL 提示符下执行：

```sql
CREATE DATABASE nav_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'nav_user'@'localhost' IDENTIFIED BY 'StrongPassword123';
GRANT ALL PRIVILEGES ON nav_db.* TO 'nav_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**注意：** 请记得修改代码中 `config.py` 里的数据库连接信息，或者设置环境变量。

## 3. 项目部署

1. **上传代码**：使用 FTP 或 SCP 将项目文件上传到 VPS（例如 `/var/www/mynav`）。

2. **创建虚拟环境**：
   ```bash
   cd /var/www/mynav
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   pip install gunicorn  # 生产环境服务器
   ```

4. **初始化数据库**：
   设置环境变量（替换为你刚才设置的密码）：
   ```bash
   export DATABASE_URL="mysql+pymysql://nav_user:StrongPassword123@localhost/nav_db"
   export SECRET_KEY="your-secret-key-here"
   flask init-db
   ```
   *这将创建默认管理员账户：用户 `admin`，密码 `admin`。请登录后尽快在数据库中修改密码或稍后添加修改密码功能。*

## 4. 运行服务 (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```
现在你可以通过 `http://你的IP:8000` 访问了。

## 5. 配置 Nginx (推荐)

安装 Nginx 并配置反向代理，以便通过域名访问。

```bash
sudo apt install nginx
```

创建配置文件 `/etc/nginx/sites-available/mynav`：

```nginx
server {
    listen 80;
    server_name your_domain.com;  # 替换为你的域名或 IP

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

启用配置并重启 Nginx：
```bash
sudo ln -s /etc/nginx/sites-available/mynav /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

## 6. 保持后台运行

使用 `systemd` 或 `supervisor` 来管理 Gunicorn 进程。

**Systemd 示例**:
创建 `/etc/systemd/system/mynav.service`:

```ini
[Unit]
Description=Gunicorn instance to serve mynav
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/mynav
Environment="PATH=/var/www/mynav/venv/bin"
Environment="DATABASE_URL=mysql+pymysql://nav_user:StrongPassword123@localhost/nav_db"
Environment="SECRET_KEY=prod-secret-key"
ExecStart=/var/www/mynav/venv/bin/gunicorn --workers 3 --bind unix:mynav.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

启动并开机自启：
```bash
sudo systemctl start mynav
sudo systemctl enable mynav
```
