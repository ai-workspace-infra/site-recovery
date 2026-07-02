# Live Environment Business Systems Topology Overview (Caddy)

By reverse-engineering the configurations under `/etc/caddy/conf.d/` and consolidating them with our latest domain-driven security architecture, the production environment's business systems have been reorganized into three core domains. All services now strictly bind to localhost (`127.0.0.1`) and stateful services connect to isolated PostgreSQL databases using least-privilege dedicated user accounts.

## 1. AI Workspace Domain
Focuses on core AI and workflow agent services.

| Business System | Exposed Domain | Internal Proxy Target (Upstream) | Description |
| :--- | :--- | :--- | :--- |
| API Gateway | `apigateway.svc.plus` | `127.0.0.1:9080` | General API Gateway |
| LiteLLM (API) | `api.svc.plus` | `127.0.0.1:4000` | Unified model routing & OpenAI/Anthropic path compatibility layer |
| LiteLLM (UI) | `litellm.svc.plus` | `127.0.0.1:4000` | LiteLLM Admin UI / Dashboard |
| OpenClaw (Bot) | `openclaw.svc.plus` | `127.0.0.1:18789` | Chatbot Backend Service (API connection to QMD) |
| RAG / QMD | `rag-server.svc.plus`<br>`rag-server-contabo-*.svc.plus` | `127.0.0.1:18084` | Retrieval-Augmented Generation Backend (pgvector enabled) |
| XWorkmate Bridge | `xworkmate-bridge.svc.plus` | `127.0.0.1:8787` | Workflow Bridge with Bearer Token strict authentication |
| Hermes | `hermes.svc.plus` | `127.0.0.1:18180` | Message Notification Gateway |

## 2. Web SaaS Domain
Includes user-facing frontends, account billing flows, and network acceleration pools.

| Business System | Exposed Domain | Internal Proxy Target (Upstream) | Description |
| :--- | :--- | :--- | :--- |
| Console | `console.svc.plus` | `127.0.0.1:3000` | AI Workspace Main Control Panel (Connects to Accounts/Billing backends) |
| Accounts | `accounts.svc.plus` | `127.0.0.1:18081` | Unified Account Management Service |
| Billing | `billing.svc.plus` | Dynamic internal ports | Billing and Payment Gateway (Stripe-pay integration) |
| Install Scripts | `install.svc.plus` | `302 Redir -> Github` | Short link distribution for curl-based one-click installation scripts |
| Ebook | `ebook.svc.plus` | Static Files | Modern IT History E-book (`/opt/modern-it-history/current`) |
| Docs | `docs.svc.plus` | `127.0.0.1:18083` | System Help Documentation |
| JP XHTTP / Xray | `jp-xhttp.svc.plus` | `/dev/shm/xray.sock` | Cross-border Network Proxy Tunnel & Acceleration Pool |
| ~~Accounts (Preview)~~| ~~`accounts-preview...`~~ | ~~`127.0.0.1:28081`~~ | ⚠️ **[Planned for Deprecation]** Testing environment |

## 3. Open Platform Infra Domain
Provides the universal foundational infrastructure, IAM, and observability stack.

| Business System | Exposed Domain | Internal Proxy Target (Upstream) | Description |
| :--- | :--- | :--- | :--- |
| Vault | `vault.svc.plus` | `127.0.0.1:8200` | Unified Credentials & Secrets Persistence (Production mode, Root token stripped) |
| Zitadel | `zitadel.svc.plus` | Container Port Mapping | IAM Global SSO (API & UI) |
| Gitea | `gitea.svc.plus` | `127.0.0.1:3001` | Private Git Code Hosting Platform |
| PostgreSQL Tunnel | `postgresql-contabo...` | Static 200 Response | Pure TLS handshake network probe (DB public access is strictly prohibited) |
| ~~Code Server~~ | ~~`observability.../code/`~~ | ~~`127.0.0.1:8443`~~ | ⚠️ **[Planned for Deprecation]** Web-based VSCode Environment |
| ~~Jupyter Lab~~ | ~~`observability.../jupyter/`~~| ~~`127.0.0.1:8888`~~ | ⚠️ **[Planned for Deprecation]** Jupyter Environment |

### 3.1 Observability Stack
`observability.svc.plus` serves as the global entry point for all monitoring components, routing based on Path:

| Path Rule | Internal Proxy Target (Upstream) | Component / Purpose |
| :--- | :--- | :--- |
| `/grafana/*` | `127.0.0.1:3000` | Grafana Visualization Dashboard (Also default root redirect) |
| `/ingest/metrics/*`<br>`/vmetrics/*` | `127.0.0.1:8428` | VictoriaMetrics (Prometheus Metrics Ingestion & Query) |
| `/ingest/logs/*`<br>`/vlogs/*` | `127.0.0.1:9428` | VictoriaLogs / Loki (Logs Ingestion & Query) |
| `/ingest/otlp/*`<br>`/vtraces/*` | `127.0.0.1:4318 / 10428` | OpenTelemetry Distributed Tracing |
| `/vmalert/*` | `127.0.0.1:8880` | VictoriaMetrics Alerting Engine |
| `/alertmgr/*` | `127.0.0.1:9059` | Alertmanager Routing & Dispatch |
| `/blackbox/*` | `127.0.0.1:9115` | Blackbox Exporter Network Probing |
| ~~`/insight/*`~~ | ~~`127.0.0.1:8082`~~ | ⚠️ **[Planned for Deprecation]** Insight Workbench Data Analysis Desk |

## 4. Deprecated Infrastructure
| Business System | Exposed Domain | Internal Proxy Target (Upstream) | Description |
| :--- | :--- | :--- | :--- |
| ~~X-Cloud-Flow~~ | ~~`x-cloud-flow.svc.plus`~~ | ~~`127.0.0.1:18083/18087`~~ | ⚠️ **[Planned for Deprecation]** Cloud Flow Control Engine |
| ~~X-Ops-Agent~~ | ~~`x-ops-agent.svc.plus`~~ | ~~`127.0.0.1:18084/18086`~~ | ⚠️ **[Planned for Deprecation]** Automated Operations Agent |
| ~~X-Scope-Hub~~ | ~~`x-scope-hub.svc.plus`~~ | ~~`127.0.0.1:18085`~~ | ⚠️ **[Planned for Deprecation]** Resource Scope Hub |
