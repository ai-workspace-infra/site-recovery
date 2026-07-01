# Site Migration & Backup Toolkit (site-migration-toolkit)

*🇨🇳 中文版在下方 | Chinese version below*

Welcome to the **Site Migration & Backup Toolkit**. This repository provides the orchestrations, runbooks, and automated playbooks for managing the disaster recovery lifecycle of the AI Workspace infrastructure.

## Phase Roadmap

This project is iteratively rolling out disaster recovery capabilities. Currently, we are heavily focused on **Phase 1**.

### Phase 1: Migration / Cold Backup / Offline Restore (Current)

Implement only the foundation:

* Ansible automated migration skeleton
* File and configuration packaging
* PostgreSQL dump / restore skeleton
* Vault secret migration design placeholder
* DNS cutover pre-check placeholder
* GitHub Actions regression verification skeleton
* Manual recovery fallback scripts and runbook

### Phase 2: Warm Standby / Scheduled Backup

Only reserve documentation and interface placeholders for:

* Scheduled backup
* Incremental sync
* Object storage archive
* Restore drill
* RPO / RTO report

### Phase 3: Hot Backup / DTS / Replication

Only reserve roadmap placeholders for:

* PostgreSQL streaming replication
* Redis replication
* DTS / CDC
* Dual-write validation
* Failover plan

### Phase 4: Multi-Active / DR Platform

Only reserve roadmap placeholders for:

* Multi-region deployment
* Traffic routing
* Data consistency strategy
* Active-Active / Active-Passive
* DR orchestration platform

### ⚠️ CI/CD Prerequisites (Important Notice)

If you are running the GitHub Actions workflow (`deploy-env-migration.yaml`), please ensure that your Vault environment is correctly configured:
- **Vault Role**: The required role name is `github-actions-site-migration-toolkit`.
- **Role Binding**: Ensure the JWT `bound_claims` match the new repository name (`repo:ai-workspace-infra/site-migration-toolkit:ref:refs/heads/main` or similar).

### 🔐 Vault Provisioning & Verification Runbook

To avoid CLI parsing issues and ensure the CI pipeline has the exact permissions it needs, follow this step-by-step runbook to provision the Vault environment.

#### Step 1: Create the Vault Policy
Create a policy that explicitly grants read access to the required secrets:
```bash
vault policy write github-actions-site-migration-toolkit - <<EOF
path "kv/data/CICD" {
  capabilities = ["read"]
}
path "kv/data/openclaw" {
  capabilities = ["read"]
}
EOF
```

#### Step 2: Verify Policy Creation
Ensure the policy was successfully written to the Vault server:
```bash
vault policy list
# Expected output should include: github-actions-site-migration-toolkit

# (Optional) Read the policy to verify its rules:
vault policy read github-actions-site-migration-toolkit
```

#### Step 3: Create the Vault JWT Role
Bind the GitHub repository identity directly to the newly created policy:
```bash
vault write auth/jwt/role/github-actions-site-migration-toolkit - <<EOF
{
  "bound_audiences": ["vault"],
  "bound_claims_type": "glob",
  "bound_claims": {
    "repository": "ai-workspace-infra/site-migration-toolkit"
  },
  "user_claim": "actor",
  "role_type": "jwt",
  "policies": ["github-actions-site-migration-toolkit"], 
  "ttl": "1h"
}
EOF
```

### 🐛 Common Vault Authentication Issues (Troubleshooting)

- **`400 Bad Request` (role could not be found)**: 
  - *Cause*: The `VAULT_ROLE` defined in `.github/workflows/deploy-env-migration.yaml` does not match any existing role in your Vault server.
  - *Fix*: Create the role using Step 3 above. Ensure the name is exactly `github-actions-site-migration-toolkit`.
- **`403 Forbidden` (during Get Vault Secrets)**: 
  - *Cause*: The JWT authenticated successfully, but the token lacks read permissions for the requested KV paths (e.g., `kv/data/CICD`). This happens if the assigned `policies` in your Role do not exist or lack the `read` capability.
  - *Fix*: Run `vault policy list` to verify. If missing, follow Step 1 and 2 to create the policy, then re-run Step 3 to ensure the Role binds to it.

---

# 站点迁移与备份工具集 (Site Migration & Backup Toolkit)

欢迎使用 **Site Migration & Backup Toolkit**。本代码库提供了管理 AI Workspace 基础架构灾难恢复生命周期的编排、运维手册和自动化 Playbooks。

## 阶段演进路线图 (Phase Roadmap)

本项目正在迭代推出灾备能力。目前，我们正重点聚焦于 **Phase 1 (第一阶段)**。

### Phase 1: 迁移 / 冷备 / 离线恢复 (当前阶段)

仅实现基础底座：

* Ansible 自动化迁移骨架
* 文件与配置打包
* PostgreSQL 逻辑备份 / 还原骨架
* Vault 凭证迁移设计占位符
* DNS 流量切换前置检查占位符
* GitHub Actions 回归验证骨架
* 手动恢复降级脚本与运维手册

### Phase 2: 温备 / 定时备份

仅保留文档与接口占位符：

* 定时计划备份
* 增量同步
* 对象存储归档
* 还原演练
* RPO / RTO 报告

### Phase 3: 热备 / DTS / 复制

仅保留路线图占位符：

* PostgreSQL 流复制
* Redis 数据复制
* DTS / CDC (变更数据捕获)
* 双写验证
* 故障转移 (Failover) 计划

### Phase 4: 多活 / 灾备管理平台

仅保留路线图占位符：

* 多地域 (Multi-region) 部署
* 流量智能路由
* 数据一致性策略
* 双活 (Active-Active) / 主备 (Active-Passive)
* DR 灾备编排平台

### ⚠️ CI/CD 前置条件 (重要提示)

如果您正在运行 GitHub Actions 流水线 (`deploy-env-migration.yaml`)，请确保您的 Vault 环境已正确配置：
- **Vault 角色 (Role)**: 所需的角色名为 `github-actions-site-migration-toolkit`。
- **角色绑定 (Role Binding)**: 请确保 JWT 的 `bound_claims` 匹配新的代码库名称（例如 `repo:ai-workspace-infra/site-migration-toolkit:ref:refs/heads/main`）。

### 🔐 Vault 鉴权配置与验证手册 (Runbook)

为了避免 Vault CLI 在解析命令行 Map 类型时出现报错，并确保流水线拥有精确且正确的权限，请按照以下标准手册 (Runbook) 逐步配置 Vault 环境。

#### 步骤 1：创建 Vault Policy
创建一个专门的 Policy，显式授予访问必需敏感信息的读权限：
```bash
vault policy write github-actions-site-migration-toolkit - <<EOF
path "kv/data/CICD" {
  capabilities = ["read"]
}
path "kv/data/openclaw" {
  capabilities = ["read"]
}
EOF
```

#### 步骤 2：验证 Policy 是否生效
确认该 Policy 已经被成功写入 Vault 服务器：
```bash
vault policy list
# 正常预期下，输出结果中必须包含: github-actions-site-migration-toolkit

# (可选) 你可以进一步读取该 Policy 的内容以确认权限细节:
vault policy read github-actions-site-migration-toolkit
```

#### 步骤 3：创建 Vault JWT Role
将 Github 代码库的身份标识（JWT Claim）与刚刚创建的权限 Policy 进行强绑定：
```bash
vault write auth/jwt/role/github-actions-site-migration-toolkit - <<EOF
{
  "bound_audiences": ["vault"],
  "bound_claims_type": "glob",
  "bound_claims": {
    "repository": "ai-workspace-infra/site-migration-toolkit"
  },
  "user_claim": "actor",
  "role_type": "jwt",
  "policies": ["github-actions-site-migration-toolkit"], 
  "ttl": "1h"
}
EOF
```

### 🐛 常见 Vault 鉴权排错指南 (Troubleshooting)

- **报错 `400 Bad Request` (role could not be found)**: 
  - *原因*: Github Actions 流水线中定义的 `VAULT_ROLE` 在你的 Vault 服务器上不存在。
  - *解法*: 请使用上方【步骤 3】的脚本创建名为 `github-actions-site-migration-toolkit` 的角色。
- **报错 `403 Forbidden` (发生在 Get Vault Secrets 阶段)**: 
  - *原因*: JWT 登录成功，但是签发的 Token 没有对应路径（如 `kv/data/CICD`）的读权限。这通常是因为绑定在 Role 上的 `policies` 不存在，或者里面的权限配置不包含 `read`。
  - *解法*: 在服务端运行 `vault policy list` 检查。如果缺少对应策略，请完整执行上方的【步骤 1 到 步骤 3】，补充权限并确保 Role 正确绑定了该 Policy。
