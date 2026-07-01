# Live Environment Business Systems Topology Overview (Caddy)

By reverse-engineering the configurations under `/etc/caddy/conf.d/` on the `install.svc.plus` node, I have outlined all business systems currently running in the production environment, their corresponding domains, and internal port mappings.

## 1. Core AI Infrastructure

| Business System | Exposed Domain | Internal Proxy Target (Upstream) | Description |
| :--- | :--- | :--- | :--- |
| API Gateway | `apigateway.svc.plus` | `127.0.0.1:9080` | General API Gateway |
| LiteLLM (API) | `api.svc.plus` | `127.0.0.1:4000` | Unified model routing & OpenAI/Anthropic path compatibility layer |
| LiteLLM (UI) | `litellm.svc.plus` | `127.0.0.1:4000` | LiteLLM Admin UI / Dashboard |
| OpenClaw (Bot) | `openclaw.svc.plus` | `127.0.0.1:18789` | OpenClaw Chatbot Backend Service |
| RAG Server | `rag-server.svc.plus`<br>`rag-server-contabo-*.svc.plus` | `127.0.0.1:18084` | RAG (Retrieval-Augmented Generation) Backend |
| XWorkmate Bridge | `xworkmate-bridge.svc.plus` | `127.0.0.1:8787` | Workflow Bridge with Bearer Token strict authentication |

## 2. DevOps & Tools

| Business System | Exposed Domain | Internal Proxy Target (Upstream) | Description |
| :--- | :--- | :--- | :--- |
| Gitea | `gitea.svc.plus` | `localhost:3001` | Private Git Code Hosting Platform |
| Vault | `vault.svc.plus` | `127.0.0.1:8200` | Unified Credentials & Secrets Persistence Service |
| ~~Code Server~~ | ~~`observability.svc.plus/code/`~~ | ~~`127.0.0.1:8443`~~ | ⚠️ **[Planned for Deprecation]** Web-based VSCode Development Environment |
| ~~Jupyter Lab~~ | ~~`observability.svc.plus/jupyter/`~~ | ~~`127.0.0.1:8888`~~ | ⚠️ **[Planned for Deprecation]** Data Science Jupyter Environment |

## 3. IAM & Accounts

| Business System | Exposed Domain | Internal Proxy Target (Upstream) | Description |
| :--- | :--- | :--- | :--- |
| Zitadel | `zitadel.svc.plus` | `127.0.0.1:19080/19081` | IAM Global SSO (API & UI) |
| Accounts | `accounts.svc.plus` | `127.0.0.1:18081` | Production Account Management Service |
| ~~Accounts (Preview)~~ | ~~`accounts-preview.svc.plus`~~ | ~~`127.0.0.1:28081`~~ | ⚠️ **[Planned for Deprecation]** Preview / Testing Environment Account Service (Will not be pulled up on DR node) |

## 4. Frontends & Consoles

| Business System | Exposed Domain | Internal Proxy Target (Upstream) | Description |
| :--- | :--- | :--- | :--- |
| Console | `console.svc.plus` | `127.0.0.1:3000` | AI Workspace Main Control Panel |
| Docs | `docs.svc.plus`<br>`docs-contabo-*.svc.plus` | `127.0.0.1:18083` | System Help Documentation (Reuses x-cloud-flow port) |
| Install Scripts | `install.svc.plus` | `302 Redir -> Github` | Short link distribution for curl-based one-click installation scripts |
| Ebook | `ebook.svc.plus` | Static Files | Modern IT History E-book (`/opt/modern-it-history/current`) |

## 5. Observability Stack

`observability.svc.plus` serves as the global entry point for all monitoring components, routing to different components based on Path:

| Path Rule | Internal Proxy Target (Upstream) | Component / Purpose |
| :--- | :--- | :--- |
| `/grafana/*` | `127.0.0.1:3000` | Grafana Visualization Dashboard (Also default root redirect) |
| `/ingest/metrics/*`<br>`/vmetrics/*` | `127.0.0.1:8428` | VictoriaMetrics (Prometheus Metrics Ingestion & Query) |
| `/ingest/logs/*`<br>`/vlogs/*` | `127.0.0.1:9428` | VictoriaLogs / Loki (Logs Ingestion & Query) |
| `/ingest/otlp/*`<br>`/vtraces/*` | `127.0.0.1:4318 / 10428` | OpenTelemetry Distributed Tracing |
| ~~`/insight/*`~~ | ~~`127.0.0.1:8082`~~ | ⚠️ **[Planned for Deprecation]** Insight Workbench Data Analysis Desk |
| `/vmalert/*` | `127.0.0.1:8880` | VictoriaMetrics Alerting Engine |
| `/alertmgr/*` | `127.0.0.1:9059` | Alertmanager Routing & Dispatch |
| `/blackbox/*` | `127.0.0.1:9115` | Blackbox Exporter Network Probing |

## 6. Other Infrastructure / Network Components

| Business System | Exposed Domain | Internal Proxy Target (Upstream) | Description |
| :--- | :--- | :--- | :--- |
| ~~X-Cloud-Flow~~ | ~~`x-cloud-flow.svc.plus`~~ | ~~`127.0.0.1:18083/18087`~~ | ⚠️ **[Planned for Deprecation]** Cloud Flow Control or Orchestration Engine |
| ~~X-Ops-Agent~~ | ~~`x-ops-agent.svc.plus`~~ | ~~`127.0.0.1:18084/18086`~~ | ⚠️ **[Planned for Deprecation]** Automated Operations Agent |
| ~~X-Scope-Hub~~ | ~~`x-scope-hub.svc.plus`~~ | ~~`127.0.0.1:18085`~~ | ⚠️ **[Planned for Deprecation]** Resource Scope Hub |
| Hermes | `hermes.svc.plus` | `127.0.0.1:18180` | Message Notification Gateway |
| JP XHTTP / Xray | `jp-xhttp.svc.plus` | `/dev/shm/xray.sock` | Cross-border Network Proxy Tunnel (gRPC) |
| PostgreSQL Tunnel | `postgresql-contabo...` | Static 200 Response | Serves purely as a TLS handshake network probe or specific proxy entry |
