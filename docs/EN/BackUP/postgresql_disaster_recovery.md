# Unified DB Backup & DR Plan

This document is based on the actual deployment of the `install.svc.plus` production environment. It outlines the standard operating procedures for the global PostgreSQL database backup, restoration, and Disaster Recovery (DR).

## 1. Production Database Architecture Checklist

Based on the production environment reconnaissance, there are currently **three independently running PostgreSQL instances**. When performing unified backups, data must be exported from these three instances separately.

| Instance Purpose | Runtime Mode | Listen Port/Address | Contained Business Databases |
| :
