# Full-Site Unified Backup & DR Plan

This document is based on the actual deployment of the `install.svc.plus` (or `root@install.svc.plus`) production environment. It outlines the global Disaster Recovery (DR) standard operating procedures. In addition to the core PostgreSQL databases, this plan covers all core stateful components required for AI Workspace to run (including application attachments, private images, VPN configurations, etc.).

## 1. Core Stateful Components & Directory Checklist

When performing cross-datacenter/cross-zone full-machine migrations, the integrity of the following data must be ensured.

### 1.1 Database Assets

| Instance Purpose | Runtime Mode | Listen Port/Address | Contained Business Databases |
| :
