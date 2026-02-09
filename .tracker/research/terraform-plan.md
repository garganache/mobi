# Terraform Plan for Scaleway Mobi Infrastructure

This document defines a **step‑by‑step, implementation‑ready plan** for creating Terraform code that provisions the architecture you described on Scaleway (dev environment first, then staging/prod):

- Svelte frontend
- FastAPI backend (orchestrator)
- PostgreSQL + JSONB
- Redis (Streams / PubSub)
- Object Storage for media
- Worker pods: Video/3D, Photo/Vision, Document/Sketch, Public Data
- External APIs: ANCPI, Seismic Risk

Each phase below is broken into **steps** and then into **tiny tasks** that you (or sub‑agents) can follow mechanically when writing Terraform.

> **Convention for this plan**
> - "Module" = a Terraform module in `infra/terraform/modules/<name>`
> - "Stack" / "Environment" = a root config in `infra/terraform/envs/<env>` (e.g. `dev`, `staging`, `prod`)
> - We will assume Scaleway provider is used and that Kubernetes manifests may be applied via Terraform or separately (but infra for K8s is managed via Terraform).

---

## Phase 1 – Repository & Terraform Layout

### Step 1.1 – Create Terraform folder structure

**Goal:** Have a clean, standardized layout for infra code.

**Tiny tasks:**
1. Create base directory structure:
    - `infra/terraform/`
    - `infra/terraform/envs/`
    - `infra/terraform/modules/`
2. Under `modules/`, create empty placeholders for planned modules:
    - `modules/project/`
    - `modules/network/`
    - `modules/object_storage/`
    - `modules/postgres/`
    - `modules/redis/`
    - `modules/kubernetes_cluster/`
    - `modules/app_backend/` (FastAPI + ingress wiring)
    - `modules/app_workers/` (worker deployments + config)
    - `modules/app_frontend/` (S3+CDN or other hosting)
    - `modules/external_apis/` (for secrets & config related to ANCPI / Seismic Risk)
3. For each module directory, add a minimal scaffold:
    - `main.tf`
    - `variables.tf`
    - `outputs.tf`
    - `README.md` (brief description of what the module manages)
4. Under `envs/`, create environment folders:
    - `envs/dev/`
    - `envs/staging/` (optional for later)
    - `envs/prod/` (for future)
5. In each env folder, create:
    - `main.tf`
    - `providers.tf`
    - `backend.tf` (for remote state, if used)
    - `variables.tf`
    - `terraform.tfvars` (git‑ignored if it will contain secrets).

### Step 1.2 – Initialize Git ignores & formatting

**Goal:** Avoid committing junk and ensure stable formatting.

**Tiny tasks:**
1. Create or update root `.gitignore` to include:
    - `.terraform/`
    - `*.tfstate`
    - `*.tfstate.backup`
    - `crash.log`
    - `.terraform.tfstate*`
    - `terraform.tfvars`
2. Decide on formatting rules:
    - Use `terraform fmt` as default.
3. Optionally add a simple `Makefile` in repo root:
    - Target `fmt`: `terraform fmt -recursive infra/terraform`
    - Target `validate`: `terraform validate` inside each env.

---

## Phase 2 – Scaleway Provider & Project Baseline

### Step 2.1 – Configure Scaleway provider

**Goal:** Make Terraform able to talk to Scaleway once credentials are provided.

**Tiny tasks:**
1. In `infra/terraform/envs/dev/providers.tf`:
    - Add `required_providers` block with `scaleway`.
    - Configure the `scaleway` provider with variables for:
        - `scw_access_key`
        - `scw_secret_key`
        - `scw_project_id`
        - `scw_region` (e.g. `fr-par` or `nl-ams`)
2. Mirror this setup in `envs/prod/providers.tf` but keep project id / region configurable.
3. In `variables.tf` for each env, declare variables for:
    - `scw_access_key`
    - `scw_secret_key`
    - `scw_project_id`
    - `scw_region`
4. Ensure `terraform.tfvars` (or environment variables) will be used to provide actual secrets, and that they are not committed.

### Step 2.2 – (Optional) Remote State Backend

**Goal:** Decide where Terraform state lives.

**Tiny tasks:**
1. Choose backend:
    - Option: Scaleway Object Storage S3‑compatible bucket.
2. Create (manually or via bootstrap Terraform) an infra‑admin bucket for state.
3. In `backend.tf` for each env:
    - Configure `backend "s3"` with:
        - `bucket` (state bucket name)
        - `key` (e.g. `mobi/dev/terraform.tfstate`)
        - `region`
        - `endpoint` (Scaleway S3 endpoint)
        - `skip_credentials_validation = true`
        - `skip_region_validation = true`
4. Run `terraform init` once per env to verify backend configuration.

---

## Phase 3 – Network & Security Baseline

### Step 3.1 – Network module (VPC, subnets, security groups)

**Goal:** Define a reusable network layer for all components.

**Tiny tasks:**
1. In `modules/network/main.tf`:
    - Create VPC or equivalent constructs supported by Scaleway (public/private subnets, if applicable).
    - Define subnets for:
        - `public` (ingress / load balancers)
        - `private` (DB, Redis, internal nodes)
2. In `variables.tf` of `network` module:
    - Variables for `project_id`, `region`, `env`, `cidr_blocks`, etc.
3. In `outputs.tf` of `network` module:
    - Output subnet IDs
    - Output security group IDs
    - Output network ID.
4. In `envs/dev/main.tf`:
    - Instantiate `module "network"` with chosen CIDR ranges.
5. Apply in dev:
    - `cd infra/terraform/envs/dev`
    - `terraform init`
    - `terraform plan -target=module.network`
    - `terraform apply -target=module.network`

### Step 3.2 – Security groups / firewall rules

**Goal:** Lock down access between components.

**Tiny tasks:**
1. In `network` module, define security groups:
    - `sg_public_ingress` – allows HTTPS/HTTP from the internet to load balancers / ingress.
    - `sg_k8s_nodes` – allows internal traffic between nodes and to DB/Redis.
    - `sg_db` – allows only from `sg_k8s_nodes` or specific private subnet CIDRs.
    - `sg_redis` – similar restrictions as DB.
2. Export security group IDs in `outputs.tf`.
3. Ensure rules explicitly restrict DB and Redis from public internet.

---

## Phase 4 – Object Storage (Media + Frontend)

### Step 4.1 – Object Storage Module

**Goal:** Create buckets for media and optionally frontend assets.

**Tiny tasks:**
1. In `modules/object_storage/main.tf`:
    - Define two buckets:
        - `media_bucket` (e.g. `mobi-media-<env>`)
        - `frontend_bucket` (e.g. `mobi-frontend-<env>`, optional)
2. Add configuration for:
    - Versioning (optional, nice to have for media).
    - Lifecycle rules (optional, for cleaning old versions if needed).
3. In `variables.tf`:
    - Variables: `project_id`, `env`, naming prefix.
4. In `outputs.tf`:
    - Output bucket names and endpoints.
5. From `envs/dev/main.tf`:
    - Instantiate `module "object_storage"` and pass project/region/env.
6. Plan and apply only this module initially to verify:
    - `terraform plan -target=module.object_storage`
    - `terraform apply -target=module.object_storage`

### Step 4.2 – Frontend Hosting Prep

**Goal:** Make the frontend bucket ready to serve a static website (even if CI will upload files).

**Tiny tasks:**
1. In `object_storage` module:
    - Configure `frontend_bucket` with static website / CDN if supported via Terraform resources.
2. Output necessary information for CI:
    - Bucket name
    - Upload endpoint / CDN URL.
3. Document in `modules/object_storage/README.md`:
    - How CI should upload `Svelte` build artifacts (e.g. via `aws s3 sync` compatible tooling with Scaleway endpoints).

---

## Phase 5 – Managed PostgreSQL (JSONB‑ready)

### Step 5.1 – Postgres Module

**Goal:** Provide a scalable PostgreSQL instance with connection details for apps.

**Tiny tasks:**
1. In `modules/postgres/main.tf`:
    - Define a managed PostgreSQL instance with size appropriate for dev.
    - Attach it to the **private** network (right subnets & security groups).
2. In `variables.tf`:
    - `project_id`, `region`, `env`
    - `db_name`, `db_user`, `db_password` (as variables, not hard‑coded).
3. In `outputs.tf`:
    - Output DB hostname, port, database name, username.
4. In `envs/dev/main.tf`:
    - Instantiate `module "postgres"`, wiring it to `module.network` outputs (subnets, security groups).
5. Run:
    - `terraform plan -target=module.postgres`
    - `terraform apply -target=module.postgres`

### Step 5.2 – DB secrets for applications

**Goal:** Expose DB credentials securely to Kubernetes (later phase).

**Tiny tasks:**
1. Decide where secrets live:
    - Option A: Use Terraform to create K8s secrets via `kubernetes_secret` resources.
    - Option B: Keep DB credentials in a secret manager and inject at deploy time (less Terraform coupling).
2. If using Terraform+K8s secrets:
    - Add a separate module `modules/app_secrets/` or extend `kubernetes_cluster` / `app_backend` module to create secrets from Terraform variables.
    - Ensure `.tfvars` for env are never committed.

---

## Phase 6 – Managed Redis (Streams / PubSub)

### Step 6.1 – Redis Module

**Goal:** Managed Redis instance reachable from K8s workers and backend.

**Tiny tasks:**
1. In `modules/redis/main.tf`:
    - Create a managed Redis instance.
    - Attach it to the private network and appropriate security group.
2. In `variables.tf`:
    - `project_id`, `region`, `env`
    - `redis_plan` / size configuration.
3. In `outputs.tf`:
    - Output Redis endpoint, port, and possibly password.
4. In `envs/dev/main.tf`:
    - Instantiate `module "redis"`, wiring network dependencies.
5. Plan and apply:
    - `terraform plan -target=module.redis`
    - `terraform apply -target=module.redis`

### Step 6.2 – Redis secrets for applications

**Goal:** As with DB, make connection info available to apps.

**Tiny tasks:**
1. Decide injection method (K8s secrets via Terraform vs external secret manager).
2. If K8s secrets via Terraform:
    - Add outputs from `redis` module to feed into `app_backend` and `app_workers` modules.

---

## Phase 7 – Kubernetes Cluster (Kapsule)

### Step 7.1 – Kubernetes Cluster Module

**Goal:** Provision one Kapsule cluster with node pools.

**Tiny tasks:**
1. In `modules/kubernetes_cluster/main.tf`:
    - Create a Scaleway Kapsule cluster.
    - Create a default node pool with small instance types for dev.
    - Attach to private network and public ingress as necessary.
2. In `variables.tf`:
    - `project_id`, `region`, `env`
    - `node_pool_size`, `node_type`, etc.
3. In `outputs.tf`:
    - Output cluster id
    - Output kubeconfig data (if Terraform exposes it) or at least references for external tooling.
4. In `envs/dev/main.tf`:
    - Instantiate `module "kubernetes_cluster"` with references to `network` module.
5. Run:
    - `terraform plan -target=module.kubernetes_cluster`
    - `terraform apply -target=module.kubernetes_cluster`

### Step 7.2 – Kubernetes provider configuration

**Goal:** Allow Terraform to manage K8s resources (optional, but useful).

**Tiny tasks:**
1. In `envs/dev/providers.tf`:
    - Add `kubernetes` and `helm` providers.
    - Configure them to use the cluster credentials from `kubernetes_cluster` outputs or from a local kubeconfig.
2. Test provider:
    - Create a trivial `kubernetes_namespace` resource in a test module.
    - Run plan/apply to ensure Terraform can talk to the cluster.

---

## Phase 8 – Backend (FastAPI) Infrastructure via Terraform

> Note: Terraform will manage infra aspects (namespaces, services, ingress, configmaps, maybe deployments). Your CI will build/push Docker images; Terraform will reference image tags.

### Step 8.1 – Backend module skeleton

**Goal:** A module that defines K8s resources for the FastAPI orchestrator.

**Tiny tasks:**
1. In `modules/app_backend/main.tf`:
    - Create a dedicated namespace (e.g. `backend`).
    - Define a `ConfigMap` for non‑secret settings (e.g. feature flags, environment name).
    - Define a `Secret` (optional; or consumed from umbrella secrets module) with:
        - `DATABASE_URL`
        - `REDIS_URL`
        - `S3_MEDIA_BUCKET`
        - `S3_ENDPOINT`
2. Define a `Deployment` for FastAPI:
    - Container image (param via `variables.tf`): e.g. `image = var.image`.
    - Environment variables referencing secrets & configmaps.
    - Resource requests/limits.
3. Define a `Service` (ClusterIP) for FastAPI.
4. Define an `Ingress` for external access:
    - Hostname (e.g. `api.<env>.mobi.example.com` from variable).
    - TLS configuration (cert‑manager annotations if used).
5. In `variables.tf`:
    - `image`, `replicas`, `hostname`, `namespace`, DB & Redis connection info, S3 bucket name.

### Step 8.2 – Wiring backend module in dev env

**Goal:** Connect backend module to cluster, DB, Redis, and S3 outputs.

**Tiny tasks:**
1. In `envs/dev/main.tf`:
    - Instantiate `module "app_backend"` with:
        - `cluster`/`kubernetes` provider via alias if necessary.
        - DB connection info from `module.postgres`.
        - Redis connection from `module.redis`.
        - S3 media bucket from `module.object_storage`.
        - `image` tag from a variable (e.g. `var.backend_image_tag`).
2. Plan and verify that only K8s resources are being created; no unintended infra changes.
3. Apply to dev once the backend image exists.

---

## Phase 9 – Workers (VPod/IPod/DPod/PPod) via Terraform

### Step 9.1 – Workers module design

**Goal:** A single module that can create multiple worker deployments/configs parametrically.

**Tiny tasks:**
1. In `modules/app_workers/main.tf`:
    - Create namespace (e.g. `workers`).
    - Define shared `ConfigMap` with common settings (e.g. log level, env name).
    - Use `for_each` over a map of worker definitions to create:
        - One `Deployment` per worker type: `vpod`, `ipod`, `dpod`, `ppod`.
2. Each worker deployment should receive:
    - Image (common or per worker type).
    - Env vars: `REDIS_URL`, `DATABASE_URL`, `S3_MEDIA_BUCKET`, plus worker‑specific config (e.g. stream name).
    - Resource requests/limits appropriate for its workload.
3. Optionally define `HorizontalPodAutoscaler` resources per worker type.
4. In `variables.tf`:
    - `workers` map with keys `vpod`, `ipod`, `dpod`, `ppod` and per‑worker configs (image, replicas, queue name).

### Step 9.2 – Wire workers to infra in dev env

**Goal:** Deploy all 4 worker categories in dev.

**Tiny tasks:**
1. In `envs/dev/main.tf`:
    - Instantiate `module "app_workers"` with:
        - DB/Redis/S3 outputs from earlier modules.
        - A `workers` map describing each worker.
2. Plan/apply after backend is working:
    - `terraform plan -target=module.app_workers`
    - `terraform apply -target=module.app_workers`

---

## Phase 10 – Frontend Hosting via Terraform

### Step 10.1 – Frontend module (static hosting)

**Goal:** Make the Svelte app reachable via a clean domain.

**Tiny tasks:**
1. In `modules/app_frontend/main.tf`:
    - Reference `frontend_bucket` from `object_storage` module (or accept as input).
    - Optionally create a CDN / static website config.
2. In `variables.tf`:
    - `domain_name` (e.g. `app.<env>.mobi.example.com`).
    - `bucket_name`.
3. If Scaleway has Terraform resources for DNS:
    - Create DNS `CNAME` record to point domain to CDN or bucket endpoint.
4. Add outputs for:
    - `frontend_url`
    - `bucket_name` for CI.

### Step 10.2 – CI integration notes (non‑Terraform but required)

**Goal:** Document how CI uploads built assets to the bucket.

**Tiny tasks:**
1. In `modules/app_frontend/README.md`:
    - Describe the exact `aws s3 sync` or equivalent command to upload `dist/` to the bucket using Scaleway S3 endpoint.
2. Note that Terraform is responsible for infra only; build and upload steps are CI’s responsibility.

---

## Phase 11 – External APIs Configuration (ANCPI, Seismic Risk)

### Step 11.1 – Secrets and config for external APIs

**Goal:** Model external API keys/URLs via Terraform without hard‑coding.

**Tiny tasks:**
1. In `modules/external_apis/main.tf`:
    - Option A: Only define Kubernetes `Secret` and/or `ConfigMap` resources that store:
        - `ANCPI_BASE_URL`, `ANCPI_API_KEY` (if used)
        - `SEISMIC_API_URL`, `SEISMIC_API_KEY` (if used)
2. In `variables.tf`:
    - Variables for URLs and keys (values passed from `env` level, never committed).
3. Wire `external_apis` module into `app_workers` and/or `app_backend` as input for environment variables.

### Step 11.2 – Wiring to PPod worker

**Goal:** Ensure PPod has all info needed for verification calls.

**Tiny tasks:**
1. In `modules/app_workers`:
    - Make PPod deployment reference secrets created in `external_apis` module.
2. In `envs/dev/main.tf`:
    - Instantiate `module "external_apis"` and pass outputs to `app_workers` (e.g. secret names).

---

## Phase 12 – Observability & Ops

### Step 12.1 – Logging & metrics modules (optional but recommended)

**Goal:** Add basic observability tooling via Terraform.

**Tiny tasks:**
1. Decide stack (e.g. Prometheus/Grafana via Helm charts, Scaleway logging integration).
2. Create a new module `modules/observability/` if necessary.
3. Use `helm_release` or K8s manifests to deploy logging/metrics stack.
4. Hook into Kapsule cluster via Terraform `helm` provider.

### Step 12.2 – Health checks and readiness

**Goal:** Encode minimal K8s health checks in Terraform.

**Tiny tasks:**
1. In `app_backend` module:
    - Add `livenessProbe` and `readinessProbe` for FastAPI container.
2. In `app_workers` module:
    - Add basic `livenessProbe` (e.g. TCP check to Redis or HTTP check, depending on implementation).

---

## Phase 13 – Environments & Promotion Workflow

### Step 13.1 – Parameterize for multiple envs

**Goal:** Make it easy to reuse modules for `dev`, `staging`, `prod`.

**Tiny tasks:**
1. Ensure all environment‑specific values are driven by variables:
    - Naming prefixes
    - Resource sizes (DB, Redis, node pool)
    - Domains
    - Docker image tags.
2. In `envs/prod/main.tf`:
    - Instantiate the same modules as in `dev`, but with higher sizes and different domain names.
3. Use `terraform.workspace` or separate state per env as needed.

### Step 13.2 – Git/CI workflow

**Goal:** Define how changes go from PR → apply.

**Tiny tasks:**
1. Document in `infra/terraform/README.md`:
    - How to run `terraform plan` locally.
    - How CI runs `terraform plan` on PR and `apply` on merge.
2. Add a simple CI workflow (YAML file) to:
    - Check formatting (`terraform fmt -check`).
    - Run `terraform validate` for each env.
    - Optionally run `terraform plan` and upload the plan file as artifact.

---

## Phase 14 – Final Verification Checklist

### Step 14.1 – Infra smoke tests

**Goal:** Verify that all pieces managed by Terraform exist and connect.

**Tiny tasks:**
1. After initial apply in dev:
    - Confirm buckets created and reachable.
    - Confirm DB instance is up and reachable from a pod.
    - Confirm Redis is reachable from a pod.
    - Confirm FastAPI pod is running and accessible via Ingress.
    - Confirm worker pods are running and can connect to Redis/DB.
2. Execute a test flow manually:
    - Upload a dummy media item via frontend or curl.
    - Verify task row appears in DB.
    - Verify worker processes the task and updates JSONB.
    - Verify updates reach frontend via SSE/WebSocket.

### Step 14.2 – Documentation

**Goal:** Make the Terraform stack maintainable by future you / others.

**Tiny tasks:**
1. Create `infra/terraform/README.md` summarizing:
    - Module layout
    - How to add a new environment
    - How to add new worker types.
2. In each module `README.md`:
    - Document inputs, outputs, and example usage snippet from `envs/*/main.tf`.

---

This plan is intentionally detailed so that you or any sub‑agent can implement each phase in small, verifiable steps without guessing. The next concrete action after reviewing this plan is to scaffold the directory structure in `infra/terraform/` (Phase 1), then gradually implement modules in the order above.
