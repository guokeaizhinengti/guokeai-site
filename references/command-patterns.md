# 部署命令骨架

## 目录

- 使用规则
- GitHub Deploy Key
- 拉取与构建
- systemd
- PM2
- Nginx
- 验证与更新

## 使用规则

以下是 Ubuntu/Linux 常见骨架，不是可盲贴的完整脚本。先从项目和服务器确认所有 `<PLACEHOLDER>`，再逐段执行并验证。其他系统使用对应包管理器和服务管理器。

## GitHub Deploy Key

在服务器部署用户下创建专用只读身份：

```bash
ssh-keygen -t ed25519 -C "<PROJECT>-deploy" -f ~/.ssh/<PROJECT>_deploy -N ""
cat ~/.ssh/<PROJECT>_deploy.pub
```

只把 `.pub` 内容添加到 GitHub 仓库 Deploy keys，不勾选写权限。不要输出私钥。

为单仓库配置别名：

```sshconfig
Host github-<PROJECT>
    HostName github.com
    User git
    IdentityFile ~/.ssh/<PROJECT>_deploy
    IdentitiesOnly yes
```

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config ~/.ssh/<PROJECT>_deploy
chmod 644 ~/.ssh/<PROJECT>_deploy.pub
ssh -T git@github-<PROJECT>
git ls-remote git@github-<PROJECT>:<OWNER>/<REPO>.git
```

## 拉取与构建

```bash
sudo install -d -o <DEPLOY_USER> -g <DEPLOY_GROUP> /opt/<PROJECT>
git clone --branch <BRANCH> git@github-<PROJECT>:<OWNER>/<REPO>.git /opt/<PROJECT>
cd /opt/<PROJECT>
git rev-parse HEAD
```

使用项目锁文件对应的确定性安装方式，例如 Node 项目优先 `npm ci`，再执行仓库定义的测试和构建命令。不要自行猜测工作目录或产物目录。

## systemd

systemd 适合不需要额外 Node 进程工具的长期服务：

```ini
[Unit]
Description=<PROJECT> application
After=network.target

[Service]
Type=simple
User=<DEPLOY_USER>
Group=<DEPLOY_GROUP>
WorkingDirectory=/opt/<PROJECT>/<SERVER_DIR>
EnvironmentFile=/etc/<PROJECT>/<PROJECT>.env
ExecStart=<ABSOLUTE_START_COMMAND>
Restart=on-failure
RestartSec=5
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now <SERVICE_NAME>
sudo systemctl status <SERVICE_NAME> --no-pager
journalctl -u <SERVICE_NAME> -n 100 --no-pager
```

## PM2

项目已采用 PM2 或团队熟悉 Node 生态时再使用：

```bash
cd /opt/<PROJECT>/<SERVER_DIR>
pm2 start <START_TARGET> --name <SERVICE_NAME>
pm2 save
pm2 startup
pm2 status
pm2 logs <SERVICE_NAME> --lines 100
```

执行 `pm2 startup` 输出的精确命令，并在部署用户身份下保存进程列表。不要同时用 systemd 和 PM2 重复守护同一个进程。

## Nginx

SPA + API 的最小骨架：

```nginx
server {
    listen 80;
    server_name <DOMAIN>;

    root /opt/<PROJECT>/<CLIENT_DIST>;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:<APP_PORT>/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:<APP_PORT>/health;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

先验证再加载：

```bash
sudo nginx -t
sudo systemctl reload nginx
curl -i -H "Host: <DOMAIN>" http://127.0.0.1/
curl -i -H "Host: <DOMAIN>" http://127.0.0.1/health
```

`proxy_pass` 尾部斜杠会影响路径拼接。根据后端实际路由验证，不要机械复制。

## 验证与更新

```bash
curl -i http://127.0.0.1:<APP_PORT>/health
curl -I http://<PUBLIC_IP>/
dig +short <DOMAIN>
curl -I http://<DOMAIN>/
curl -I https://<DOMAIN>/
```

更新时固定目标提交：

```bash
cd /opt/<PROJECT>
git fetch --prune origin
git checkout <BRANCH>
git pull --ff-only origin <BRANCH>
git rev-parse HEAD
```

随后按锁文件安装、构建、重启、健康检查和核心功能冒烟。记录部署前 SHA；回滚时检出已知可运行 SHA 或切回上一发布目录，不使用破坏性 Git 命令清除未知改动。
