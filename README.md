# ForestNav VPS 部署完整指南 (Ubuntu/Debian)

本指南针对**Ubuntu 20.04/22.04**系统，使用 **Nginx + Gunicorn** 部署 Flask 应用。我们将使用默认的 **SQLite** 数据库，适合个人导航站。

---

## 1. 基础环境准备

SSH 登录到你的 VPS，执行以下命令更新系统并安装基础组件。

```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装 Python3, pip, venv 和 Nginx
sudo apt install python3-pip python3-venv nginx git -y
```

## 2. 上传代码与虚拟环境

我们假设将代码部署在 `/var/www/forestnav` 目录。

### 步骤 A: 上传/克隆代码
你可以使用 Git 克隆（推荐），或者使用 SCP/SFTP 上传代码。

**方式 1 (Git - 推荐):**
```bash
# 创建目录并设置权限
sudo mkdir -p /var/www/forestnav
sudo chown -R $USER:$USER /var/www/forestnav

# 进入目录
cd /var/www/forestnav

# 如果你是从 GitHub 拉取
# git clone https://github.com/yourusername/repo.git .

# 如果你是本地上传，请使用 FTP/SFTP 工具将文件夹内容上传到此目录
```

### 步骤 B: 设置 Python 环境
```bash
cd /var/www/forestnav

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖 (确保 requirements.txt 在目录下)
pip install -r requirements.txt

# 安装生产环境 Web 服务器 Gunicorn
pip install gunicorn
```

### 步骤 C: 初始化数据库
```bash
# 确保在虚拟环境中
export FLASK_APP=app.py

# 进入 python shell 初始化
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"

# (可选) 如果你需要创建初始管理员用户，可以使用类似 init_db.py 的脚本，或者手动通过 python shell 创建
```

## 3. 配置 Gunicorn 服务 (Systemd)

我们需要创建一个 systemd 服务文件，让应用在后台运行并在开机时自动启动。

```bash
sudo nano /etc/systemd/system/forestnav.service
```

**粘贴以下内容（请根据实际路径修改 User 和 WorkingDirectory）：**

```ini
[Unit]
Description=Gunicorn instance to serve ForestNav
After=network.target

[Service]
# 将 ubuntu 替换为你的 VPS 用户名 (例如 root 或 ubuntu)
User=root
# 组通常与用户名相同
Group=root

# 项目路径
WorkingDirectory=/var/www/forestnav
Environment="PATH=/var/www/forestnav/venv/bin"
# 这里可以设置环境变量，例如生产环境密钥
Environment="SECRET_KEY=your-super-secret-production-key-change-this"

# 启动命令 (运行在 8000 端口)
ExecStart=/var/www/forestnav/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
```

**启动服务：**
```bash
# 启动并设置开机自启
sudo systemctl start forestnav
sudo systemctl enable forestnav

# 检查状态 (确保显示 active (running))
sudo systemctl status forestnav
```

## 4. 配置 Nginx 反向代理

Nginx 将作为前置服务器，处理 HTTP 请求并转发给 Gunicorn。

```bash
sudo nano /etc/nginx/sites-available/forestnav
```

**粘贴以下内容（修改 server_name 为你的域名或 IP）：**

```nginx
server {
    listen 80;
    # 填写你的域名，如果没有域名则填写服务器公网 IP
    server_name example.com www.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_include /etc/nginx/proxy_params;
        proxy_redirect off;
        
        # 传递真实 IP
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件长期缓存 (可选)
    location /static {
        alias /var/www/forestnav/static;
        expires 30d;
    }
}
```

**激活配置并重启 Nginx：**
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/forestnav /etc/nginx/sites-enabled

# 检查配置语法
sudo nginx -t

# 如果通过检查，重启 Nginx
sudo systemctl restart nginx
```

## 5. 配置 HTTPS (强烈推荐)

如果有域名，可以使用 Certbot 免费申请 SSL 证书。

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 自动配置 HTTPS
sudo certbot --nginx -d example.com -d www.example.com
```

---

## 常用维护命令

- **重启应用 (代码更新后)**: `sudo systemctl restart forestnav`
- **查看应用日志**: `journalctl -u forestnav -f`
- **重启 Nginx**: `sudo systemctl restart nginx`
