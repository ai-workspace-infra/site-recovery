# 全站统一备份与灾备方案 (AI Workspace)

本文档基于 `install.svc.plus` (或 `root@install.svc.plus`) 线上环境的实际部署情况，为你规划和整理了全局的灾备（DR）标准操作流程。 除了核心的 PostgreSQL 数据库外，本方案覆盖了 AI Workspace 运行所需的所有核心状态组件（含应用附件、私有镜像、VPN 配置等）。

## 1. 核心状态组件与目录清单

在进行跨机房/跨区整机迁移时，必须确保以下数据的完整迁移。

### 1.1 数据库资产

| 实例用途 | 运行模式 | 监听端口/地址 | 包含的业务系统库 |
| :--- | :--- | :--- | :--- |
| AI 核心服务库 | Docker (`postgresql-svc-plus`) | `127.0.0.1:15432` | Account, Vault Storage, Artifact, LiteLLM, OpenClaw, QMD, RAG, Notification, Scheduler, Audit |
| Zitadel 认证库 | Docker (`zitadel-db-1`) | 容器内部网 | Zitadel IAM 数据 |
| Gitea 代码库 | Native Systemd (PG 16) | `127.0.0.1:5434` | Gitea 元数据 |

### 1.2 关键文件与持久化挂载卷 (Stateful Volumes)

> [!IMPORTANT]
> 以下目录是系统恢复后的“血肉”，如果不迁移，即使数据库还原，也会出现图片 404、模型拉取失败、组网断开等致命故障。

*   **Gitea 仓库与对象数据:** `/var/lib/gitea/data`
    存储所有的 Git 裸仓库、LFS 大文件、用户头像及附件。
*   **应用私有镜像库 (Harbor / Registry):** `/data/registry` 或挂载的 `/data/harbor`
    私有容器镜像。如果不迁移，新机在重启并执行 `docker-compose pull` 时将找不到未开源的基础环境镜像。
*   **OpenClaw (AI 网关) 工作目录:** `openclaw workdir` (对应部署时的物理挂载点)
    包含 AI Gateway 的本地缓存档、向量化临时数据或加载的模型资产。
*   **分布式组网与 VPN 配置:** `/etc/wireguard`
    包含本地节点的 WireGuard Private Key 与 Peers 路由表。若丢失此目录，新主机启动后将无法重新融入原有的 Xworkmate VPN 星型网络，所有跨云微服务通信将中断。
*   **对象存储 (MinIO/S3):** `/data/minio` (若开启)
    现代云原生组件（如 Wiki、RAG）的大文件存储底座。
*   **环境密钥文件:** 各组件部署目录下的 `.env` (如 `/opt/ai-workspace/`)。

> [!NOTE]
> **例外清单：** `/etc/caddy/data` 或 `acme.json`（Let's Encrypt 证书）。
> **处理策略：** 灾备演练或真实迁移时无需同步。只需在新主机上线时，提前将 DNS A 记录解析至新 IP，再启动 Caddy 即可实现全自动在线续签。（需注意 Let's Encrypt 每周 5 次的重复签发限频，演练时建议使用 Staging 证书）。

## 2. 统一备份与同步策略 (Backup & Sync)

### 2.1 数据库逻辑备份 (PostgreSQL)

建议在宿主机的 `/opt/backup/` 目录下创建统一备份脚本 `pg_backup.sh` 并加入 Cron 定时任务：

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +"%Y%m%d_%H%M%S")
mkdir -p $BACKUP_DIR

echo "[INFO] 备份 AI 核心服务库 (15432 端口)..."
DB_URL_BASE="postgres://svcplus_vps:<YOUR_PASSWORD>@127.0.0.1:15432"
for DB in account litellm openclaw qmd rag notification scheduler audit artifact vault_storage; do
    pg_dump "$DB_URL_BASE/$DB?sslmode=disable" | gzip > "$BACKUP_DIR/${DB}_$DATE.sql.gz"
done

echo "[INFO] 备份 Zitadel 认证库 (zitadel-db-1)..."
docker exec zitadel-db-1 pg_dumpall -U postgres | gzip > "$BACKUP_DIR/zitadel_$DATE.sql.gz"

echo "[INFO] 备份 Gitea 代码库 (Native PG 16)..."
sudo -u postgres pg_dumpall -p 5434 | gzip > "$BACKUP_DIR/gitea_$DATE.sql.gz"

# 清理 7 天前的旧备份
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +7 -delete
```

### 2.2 文件状态同步 (Rsync 增量同步)

针对文件资源，建议使用 `rsync` 结合 Ansible 剧本向灾备节点推送，或定时同步到集中式对象存储。 关键的 `rsync` 路径示例：

```bash
rsync -avz --delete /var/lib/gitea/data/ backup-server:/backup/gitea/
rsync -avz --delete /etc/wireguard/ backup-server:/backup/wireguard/
rsync -avz --delete /data/registry/ backup-server:/backup/registry/
```

## 3. 灾难恢复与还原操作 (Restore)

当发生整机崩溃或机房断网需要启用灾备节点时，严格按以下层级恢复：

**阶段 1: 恢复 VPN 与网络层**
在安装任何服务前，首先将 `/etc/wireguard` 目录还原，并启动 `wg-quick up wg0`，确保灾备节点重新获取原集群内网 IP。

**阶段 2: 恢复对象与文件持久层**
将备份好的 Gitea、OpenClaw workdir、应用镜像目录等还原至宿主机的绝对路径中，并修复属主权限（如 `chown -R 1000:1000 /var/lib/gitea`）。

**阶段 3: 恢复 PostgreSQL 数据库层**
确保仅启动数据库容器（停掉应用层容器）。

```bash
# 1. 还原 AI 核心库
gunzip -c /var/backups/postgresql/account_YYYYMMDD.sql.gz | psql "postgres://...:15432/account"

# 2. 还原 Zitadel 库
gunzip -c /var/backups/postgresql/zitadel_YYYYMMDD.sql.gz | docker exec -i zitadel-db-1 psql -U postgres

# 3. 还原 Gitea 库
gunzip -c /var/backups/postgresql/gitea_YYYYMMDD.sql.gz | sudo -u postgres psql -p 5434
```

**阶段 4: 启动接入层与业务应用**
1. 确认全网 DNS 已切换至当前灾备节点公网 IP。
2. 启动 Caddy 服务，系统会自动发起 HTTP-01 质询申请全新证书。
3. 全面上线 `docker-compose up -d` 拉起各业务线应用。
