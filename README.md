# guokeai-site

一个面向中文用户的网站上线向导 Skill。它会先问你选择**国内上线还是国外上线**，再把本地项目经过 GitHub 部署到对应的云服务器或托管平台，并绑定正式域名与 HTTPS。

它不是只能照抄的服务器命令清单，也不是只适用于某个框架的一键脚本。Skill 会先确定路线，再识别项目，并按照可验证的关卡一步一步推进；如果中途失败，会判断问题究竟出在代码、GitHub、托管平台、服务器、Nginx、云安全组、DNS 还是 HTTPS。

## 两条上线路线

调用 Skill 后，如果你没有提前说明，它会先问：

```text
你希望走哪条上线线路？

1. 国内上线：中国大陆境内云服务器，包含备案、云安全组、Nginx 和 HTTPS。
2. 国外上线：海外托管平台或海外服务器，包含平台选择、全球区域、域名和 HTTPS。

回复“国内”或“国外”即可。
```

### 国内上线

适合中国大陆境内云服务器，包含：

- ICP 备案/许可与接入商前置检查
- GitHub 或可审计发布制品
- Linux 运行环境和进程守护
- Nginx/Caddy、云安全组和系统防火墙
- DNS、HTTPS、证书续期和旧域名迁移
- 国内网络依赖与分层排障

### 国外上线

适合海外托管平台、中国香港及其他境外服务器，包含：

- 托管平台与自管 VPS 的选择
- GitHub 导入、预览部署和生产发布
- 构建命令、产物目录和环境变量
- 全球区域、数据库、对象存储和后台任务
- 平台自定义域名、DNS 和托管 HTTPS
- 海外 VPS 的进程守护、Nginx 和证书
- 目标地区测速、更新、回滚和合规待办

## 适合什么场景

- 第一次把本地网站部署到公网
- 从本地项目建立 GitHub 发布流程
- 部署静态站、SPA、SSR、Node/Python 后端或容器项目
- 使用国内云服务器、海外 VPS 或海外托管平台
- 配置 Nginx、进程守护、云安全组、DNS 和 HTTPS
- 排查“本地能打开，平台/服务器/域名打不开”
- 迁移服务器、平台、区域或域名
- 建立后续更新、监控和回滚流程

## 核心思路

Skill 把网站上线拆成七层：

1. **制品层**：源码能否构建成可运行产物
2. **版本层**：GitHub 是否保存准确、无秘密的指定提交
3. **运行层**：平台或服务器是否持续运行该版本
4. **入口层**：平台入口或 Nginx/Caddy 是否正确分发页面与 API
5. **网络层**：平台网络、进程监听、防火墙和公网路由是否连通
6. **身份层**：DNS 与 TLS 证书是否对应准确域名
7. **运营层**：合规、日志、监控、备份、更新和回滚是否可持续

排障时从最内层向外验证：

```text
本地生产构建
  → 平台部署或服务器健康检查
  → Web 入口
  → 平台临时域名或公网 IP
  → DNS
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

- 先选择国内或国外路线
- 只读盘点本地项目
- 验证生产构建和核心功能
- 检查秘密、锁文件和 GitHub 提交
- 选择国内服务器、海外托管平台或海外 VPS
- 部署应用并建立统一入口
- 逐层打通 DNS、HTTPS 和正式域名
- 完成日志、重启/重新部署、更新、回滚与交付清单

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

让 Skill 先询问路线：

```text
使用 $guokeai-site 带我把这个本地项目上线。
```

直接指定国内路线：

```text
使用 $guokeai-site 带我把 React + Node 项目部署到国内云服务器，
代码还没有上传 GitHub，我已经有域名。
```

直接指定国外路线：

```text
使用 $guokeai-site 带我把这个 Next.js 项目部署到国外托管平台，
先帮我判断平台部署还是海外 VPS 更合适。
```

排查问题：

```text
使用 $guokeai-site 排查：预览部署正常，但绑定正式域名后 API 不工作。
```

Skill 会优先检查当前项目，能够从仓库识别的信息不会反过来让你选择。涉及云厂商或平台控制台时，可以把截图发给助手，由助手指出当前页面应该操作的字段。

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
│   ├── global-routing.md
│   ├── command-patterns.md
│   └── troubleshooting.md
└── scripts/
    └── inspect_project.py
```

- `SKILL.md`：国内/国外首问分流、逐阶段流程与验收条件
- `principles.md`：从真实上线经历抽象出的通用原则
- `china-routing.md`：中国大陆境内服务器与备案路线
- `global-routing.md`：海外托管平台和海外 VPS 路线
- `command-patterns.md`：自管服务器的 GitHub、systemd、PM2 和 Nginx 命令骨架
- `troubleshooting.md`：平台和服务器的分层排障矩阵

## 安全原则

- 不索取或输出密码、私钥、访问令牌和真实 `.env`
- 本地、托管平台和服务器使用独立的最小权限身份
- 托管平台优先使用官方 GitHub 集成，服务器优先使用只读 Deploy Key
- 应用默认只公开必要入口，不随意开放管理端口
- 不通过关闭 TLS 校验、防火墙或 SSRF 防护来解决部署问题
- 生产变更前保留可回滚版本，变更后验证真实核心功能

涉及备案、隐私、云厂商界面和平台规则时，Skill 会要求核验当下官方信息，不把仓库中的说明当作法律意见或永久不变的平台规则。

## 贡献

欢迎提交 Issue 或 Pull Request，补充新的框架、托管平台、云厂商场景、失败案例和更安全的部署实践。请优先贡献可迁移的方法，而不是只对某一个项目有效的固定 IP、域名或命令。

## License

[MIT](LICENSE)
