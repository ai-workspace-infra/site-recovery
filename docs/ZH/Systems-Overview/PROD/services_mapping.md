# 控制面节点 (jp-xhttp-contabo) 服务链路与代理映射白皮书

本文档旨在全局梳理运行于 `console.svc.plus` (`jp-xhttp-contabo`) 节点上的所有网关代理层及其背后的真实服务进程、路径绑定关系。为故障排查、服务迁移及日志审计提供权威依据。

---

## 一、 Caddy 路由与上游服务全景映射

Caddy (`/etc/caddy/conf.d/*.caddy`) 作为全局唯一的 443 入口网关，承接着众多二级域名的流量。以下是所有域名的后端分发全名录：

| 代理配置文件名 (`*.caddy`) | 对外暴露域名 | 后端上游地址 | 底层服务形态 | 实际进程 / 容器名 |
| :--- | :--- | :--- | :--- | :--- |
| `accounts.svc.plus.caddy` | `accounts.svc.plus` | `127.0.0.1:18081` | Docker | `accounts-managed-prod-contabo` |
| `api.svc.plus.caddy` | `api.svc.plus` | `127.0.0.1:4000` | Systemd | `litellm-proxy.service` |
| `apigateway.svc.plus.caddy`| `apigateway.svc.plus`| `127.0.0.1:9080` | Docker | `svc-ai-gateway` (APISIX) |
| `code.svc.plus.caddy` | `code.svc.plus` | `localhost:3001` | Systemd | `gitea.service` |
| `console.svc.plus.caddy` | `console.svc.plus` | `127.0.0.1:3000` | Docker | `console-c894924-contabo` |
| `docs.svc.plus.caddy` | `docs.svc.plus` | `127.0.0.1:18083` | Docker | `docs-us-xhttp-c75387a` |
| `ebook.svc.plus.caddy` | `ebook.svc.plus` | *(静态目录)* | N/A | `/opt/modern-it-history/current` |
| `gitea.svc.plus.caddy` | `gitea.svc.plus` | `localhost:3001` | Systemd | `gitea.service` |
| `hermes.svc.plus.caddy` | `hermes.svc.plus` | `127.0.0.1:18180` | Systemd | `acp-hermes.service` |
| `iam.svc.plus.caddy` | `iam.svc.plus` | `19080` / `19081`| Docker | `zitadel-zitadel-1` |
| `install.svc.plus.caddy` | `install.svc.plus` | *(302 重定向)* | N/A | Githubusercontent Setup Scripts |
| `jp-xhttp.svc.plus.caddy` | `jp-xhttp.svc.plus`| `unix//dev/shm/...`| Systemd | 节点 Xray/v2ray 代理进程 |
| `litellm.svc.plus.caddy` | `litellm.svc.plus` | `127.0.0.1:4000` | Systemd | `litellm-proxy.service` |
| `observability.caddy` | `observability.svc.plus`| 多端口分发 | 混合编排 | Grafana / VictoriaMetrics / ... |
| `openclaw.svc.plus.caddy` | `openclaw.svc.plus` | `127.0.0.1:18789` | Systemd | `openclaw.service` |
| `postgresql-17...caddy` | `postgresql-17...plus`| TLS Tunnel 鉴权 | Docker | `stunnel-client` / `stunnel-server` |
| `rag-server.svc.plus.caddy`| `rag-server.svc.plus`| `127.0.0.1:18084` | Docker | `rag-server-us-xhttp-8ca3e271` |
| `vault.svc.plus.caddy` | `vault.svc.plus` | `127.0.0.1:8200` | Docker | `vault` |
| `xworkmate-bridge.caddy` | `xworkmate-bridge.svc.plus`| `127.0.0.1:8787` | Systemd | `xworkmate-bridge.service` |

---

## 二、 核心关联基建路径 (物理目录与 Compose)

对于上述被 Caddy 所引用的核心服务，其底层的编排文件或执行路径已经定位如下，供备份、排错或迁移时使用：

### 1. 静态与纯净托管服务
- **Ebook 电子书聚合** (`ebook.svc.plus`)
  - 纯静态资源挂载：`/opt/modern-it-history/current`

### 2. 容器化 (Docker Compose) 托管服务
- **IAM 认证中心 (Zitadel)** (`iam.svc.plus`)
  - 编排目录: `/opt/zitadel`
  - 关联容器: `zitadel-zitadel-1`, `login-external-tls`
- **Vault 凭证管控** (`vault.svc.plus`)
  - 编排目录: `/opt/vault`
  - 关联容器: `vault`
- **APISIX 网关** (`apigateway.svc.plus`)
  - 编排目录: `/opt/svc-ai-gateway`
  - 关联容器: `svc-ai-gateway`
- **RAG 推理服务** (`rag-server.svc.plus`)
  - 编排目录: `/opt/cloud-neutral/rag-server/rag-server-us-xhttp-8ca3e271`
  - 关联容器: `rag-server-us-xhttp-8ca3e271`
- **文档渲染中心** (`docs.svc.plus`)
  - 编排目录: `/opt/cloud-neutral/docs/docs-us-xhttp-c75387a`
  - 关联容器: `docs-us-xhttp-c75387a`

### 3. 本地原生服务 (Systemd Services)
- **Gitea 代码托管库** (`gitea.svc.plus`, `code.svc.plus`)
  - 进程控制: `gitea.service`
  - 工作目录: `/var/lib/gitea/`
- **LiteLLM 路由网关** (`litellm.svc.plus`, `api.svc.plus`)
  - 进程控制: `litellm-proxy.service`
  - 工作目录: `/home/ubuntu`
- **XWorkmate Bridge 桥接** (`xworkmate-bridge.svc.plus`)
  - 进程控制: `xworkmate-bridge.service`
  - 工作目录: `/opt/cloud-neutral/xworkmate-bridge`
- **Hermes 消息总线** (`hermes.svc.plus`)
  - 进程控制: `acp-hermes.service`

---

> [!NOTE]
> 以上所有相关的宿主机配置文件和编排目录，请参考现有的 `saas_legacy_backup_guide.md` 原则，在执行迁移时一并剥离至 Vault 或安全存储库，避免明文环境泄露。
