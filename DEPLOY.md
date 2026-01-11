# Alpha Terminal 部署指南

本指南将指导您将 Alpha Terminal 部署到 Linux 服务器（以 Ubuntu 22.04 为例）。

## 1. 准备工作

确保您有一台 Linux 服务器，并且已经安装了：
- **Python 3.9+**
- **Node.js 18+**
- **Nginx**

### 安装基础环境 (Ubuntu)
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 和 pip
sudo apt install python3-pip python3-venv -y

# 安装 Nginx
sudo apt install nginx -y

# 安装 Node.js (使用 nvm 或直接安装，这里推荐直接安装)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

## 2. 上传项目代码

将您的项目文件上传到服务器，例如上传到 `/var/www/alpha-terminal`。
推荐结构：
```
/var/www/alpha-terminal/
├── main.py
├── requirements.txt
├── config.json (如果是新建项目可能需要手动创建)
├── active_positions.json
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
└── ...
```

## 3. 部署后端 (FastAPI)

### 3.1 创建虚拟环境并安装依赖
```bash
cd /var/www/alpha-terminal

# 创建虚拟环境
python3 -m venv venv

# 激活环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3.2 配置 Systemd 守护进程
为了让后端在后台持续运行，我们需要创建一个系统服务。

```bash
sudo nano /etc/systemd/system/alpha-backend.service
```

在文件中粘贴以下内容（**注意修改路径和用户名**）：
```ini
[Unit]
Description=Alpha Terminal Backend
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/alpha-terminal
# 生产环境建议使用 gunicorn (或者直接用 uvicorn)
ExecStart=/var/www/alpha-terminal/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3.3 启动后端服务
```bash
# 重新加载配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start alpha-backend

# 设置开机自启
sudo systemctl enable alpha-backend

# 查看状态（确认是否显示 Active: active (running)）
sudo systemctl status alpha-backend
```

## 4. 部署前端 (Vue + Vite)

### 4.1 编译打包
```bash
cd /var/www/alpha-terminal/frontend

# 安装依赖
npm install

# 打包构建 (生成 dist 目录)
npm run build
```
执行完成后，您应该会在 `frontend` 目录下看到一个 `dist` 文件夹。

## 5. 配置 Nginx 反向代理

Nginx 将负责两件事：
1. 提供前端静态文件 (dist 目录)。
2. 将 `/api` 或直接请求转发给后端的 8000 端口。

**注意：** 因为您的前端直接请求的是根路径下的接口（如 `/rates_single`），我们需要配置 Nginx 将 API 请求转发给后端，将页面请求指向前端。

### 5.1 创建 Nginx 配置
```bash
sudo nano /etc/nginx/sites-available/alpha-terminal
```

粘贴以下内容：
```nginx
server {
    listen 80;
    server_name your_domain_or_ip;  # 替换为您的域名或服务器IP

    # 前端静态文件
    location / {
        root /var/www/alpha-terminal/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 转发
    # 这里我们转发所有未知的请求给后端，或者您可以列出具体的 API 路径
    # 由于 Vite 开发时配置了 proxy，生产环境我们要手动处理
    
    # 假设 API 接口都是根路径（如 /rates_single），这可能会和前端路由冲突。
    # 推荐的做法是：
    # 1. 修改前端 baseURL 为 /api
    # 2. 或者在这里明确列出 API 路径
    
    # 这里为了简便，我们将特定 API 路径转发
    location ~ ^/(rates_single|spreads_price|arb_futures|positions|check_status|execute_strategy|update_config|close_position|history_orders|lock_history_order|delete_history_order|set_mode) {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 5.2 启用配置并重启 Nginx
```bash
# 建立软链接
sudo ln -s /etc/nginx/sites-available/alpha-terminal /etc/nginx/sites-enabled/

# 检查配置是否正确
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

## 6. 完成
现在，您可以直接在浏览器访问您的服务器 IP 或域名，即可看到 Alpha Terminal。

### 常用维护命令
- 查看后端日志: `journalctl -u alpha-backend -f`
- 重启后端: `sudo systemctl restart alpha-backend`
- 修改前端后更新: 在 frontend 目录下运行 `npm run build`
