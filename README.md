# guokeai-site

一个面向国内用户的网站上线向导 Skill，带你把本地项目经过 GitHub 部署到云服务器，并绑定可公开访问的域名与 HTTPS。

它不是一份只能照抄的服务器命令清单，也不是只适用于某个框架的一键脚本。它会先识别你的项目，再按照可验证的关卡一步一步推进；如果中途失败，会判断问题究竟出在代码、GitHub、服务器、Nginx、云安全组、DNS 还是 HTTPS。

## 适合什么场景

- 第一次把本地网站部署到公网
- 从本地项目建立 GitHub 发布流程
- 部署静态站、SPA、Node/Python 后端或容器化项目
- 配置 Nginx、进程守护、云安全组、DNS 和 HTTPS
- 使用中国大陆境内服务器，并梳理 ICP 备案等前置事项
- 排查“本地能打开，服务器或域名打不开”
- 迁移服务器、域名或建立后续更新与回滚流程

## 核心思路

Skill 把网站上线拆成七层：

1. **制品层**：源码能否构建成可运行产物
2. **版本层**：GitHub 是否保存了准确、无秘密的指定提交
3. **运行层**：服务器上的应用是否持续运行并能重启恢复
4. **入口层**：Nginx/Caddy 是否正确分发页面与 API
5. **网络层**：进程监听、防火墙、云安全组和公网路由是否连通
6. **身份层**：DNS 与 TLS 证书是否对应准确域名
7. **运营层**：备案/许可、日志、监控、备份、更新和回滚是否可持续

排障时从最内层向外验证：

```text
本地生产构建
  → 服务器应用健康检查
  → Nginx 本机入口
  → 公网 IP
  → DNS
  → HTTP
  → HTTPS
  → 真实核心功能
```

上一关没有通过，就不继续修改下一层。

## 它会怎样带你上线

每一步只提供当前需要的信息：

1. 本步目标与原因
2. 针对当前项目的操作或命令
3. 应该看到的结果
4. 验证方法
5. 需要回传的输出或控制台截图

完整流程包括：

- 只读盘点本地项目
- 验证生产构建和核心功能
- 检查秘密、锁文件和 GitHub 提交
- 为本地与服务器分别配置 GitHub 身份
- 根据服务器地域分流国内上线方案
- 在服务器复现运行环境
- 配置进程守护和统一 Web 入口
- 逐层打通安全组、DNS、HTTP 和 HTTPS
- 完成日志、重启、更新、回滚与交付清单

## 安装

### Codex

macOS / Linux：

```bash
git clone https://github.com/guokeaizhinengti/guokeai-site.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/guokeai-site"
```

Windows PowerShell：

```powershell
git clone https://github.com/guokeaizhinengti/guokeai-site.git `
  "$env:USERPROFILE\.codex\skills\guokeai-site"
```

如果目标目录已经存在，请先确认里面是否有需要保留的修改，不要直接覆盖。

安装完成后重新打开 Codex 任务，技能列表中应出现 `guokeai-site`。

## 使用

直接调用：

```text
使用 $guokeai-site 带我把这个本地项目上线。
```

也可以带上已有信息：

```text
使用 $guokeai-site 带我把这个 React + Node 项目部署到腾讯云服务器，
代码还没有上传 GitHub，我已经有域名。
```

```text
使用 $guokeai-site 排查：服务器本机访问正常，但通过公网 IP 会超时。
```

Skill 会优先检查当前项目，能够从仓库识别的信息不会反过来让你选择。涉及云厂商控制台时，可以把截图发给助手，由助手指出当前页面应该操作的字段。

## 可选：本地项目盘点

仓库附带一个只读脚本，用于识别 Git 状态、常见技术栈、构建脚本、锁文件、部署配置和环境变量模板名称：

```bash
python scripts/inspect_project.py /path/to/project
```

脚本不会运行构建，不会读取真实 `.env` 的值，也不会修改项目。

## 目录结构

```text
guokeai-site/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── principles.md
│   ├── china-routing.md
│   ├── command-patterns.md
│   └── troubleshooting.md
└── scripts/
    └── inspect_project.py
```

- `SKILL.md`：逐阶段上线流程与验收条件
- `principles.md`：从真实上线经历抽象出的通用原则
- `china-routing.md`：大陆境内/境外服务器分流与官方核验原则
- `command-patterns.md`：GitHub、systemd、PM2 和 Nginx 命令骨架
- `troubleshooting.md`：按症状和层级组织的排障矩阵

## 安全原则

- 不索取或输出密码、私钥、访问令牌和真实 `.env`
- 本地开发机与服务器使用不同的 SSH 密钥
- 服务器优先使用单仓库只读 GitHub Deploy Key
- 应用默认监听回环地址，只公开必要的 80/443 端口
- 不通过关闭 TLS 校验、防火墙或 SSRF 防护来解决部署问题
- 生产变更前保留可回滚版本，变更后验证真实核心功能

涉及备案、云厂商界面和平台规则时，Skill 会要求核验当下官方信息，不把仓库中的说明当作法律意见或永久不变的平台规则。

## 贡献

欢迎提交 Issue 或 Pull Request，补充新的框架、云厂商场景、失败案例和更安全的部署实践。请优先贡献可迁移的方法，而不是只对某一个项目有效的固定 IP、域名或命令。

## License

[MIT](LICENSE)
