# Mobi Dev Environment – Current Architecture & Pipeline State (2026-02-09)

This document captures the *current* dev architecture as deployed on Scaleway, plus the CI/CD and configuration details. It’s meant as a snapshot so we can reason about changes later without re‑reverse‑engineering everything.

> Scope: **dev** environment only (Kapsule + RDB + K8s manifests + GitHub Actions).

---

## 1. Cloud & Infra Overview

### 1.1 Provider & Project

- **Cloud:** Scaleway
- **Regions:**
  - Dev infra uses `var.scw_region` (default `fr-par`).
- **Project:**
  - `scaleway_account_project` data source used in Terraform.

### 1.2 High-Level Components

- **Private Network:**
  - Terraform-managed `scaleway_vpc_private_network.dev` named `mobi-dev-private-network`.
  - Tagged `env:dev`, `app:mobi`.

- **Kubernetes Cluster (Kapsule):**
  - Terraform resource: `scaleway_k8s_cluster.dev`.
  - Name: `mobi-dev-cluster`.
  - Type: `kapsule`.
  - CNI: `cilium`.
  - Version: explicitly `1.35.0`.
  - Attached to `mobi-dev-private-network`.
  - `delete_additional_resources = true` (cluster deletion tears down dependent cloud resources).

- **Node Pool:**
  - Terraform resource: `scaleway_k8s_pool.dev_default`.
  - Name: `dev-pool`.
  - Node type: `DEV1-M`.
  - Size: `1` node.
  - Autoscaling: `false`.
  - Tags: `env:dev`, `app:mobi`.

- **Postgres (RDB):**
  - Terraform resource: `scaleway_rdb_instance.dev`.
    - Name: `mobi-dev-db`.
    - Engine: `PostgreSQL-16`.
    - Node type: `DB-DEV-S`.
    - Region: `var.scw_region` (dev region).
    - HA: `false`.
    - Tags: `env:dev`, `app:mobi`.
  - Database: `scaleway_rdb_database.mobi` (name: `mobi`).
  - User: `scaleway_rdb_user.mobi` (name: `mobi`).
    - Password: `var.mobi_db_password` (wired from `MOBI_DB_PASSWORD` secret in CI).
  - Output:
    - `output "db_connection_url"` builds a SQLAlchemy/psycopg URL from `endpoint_ip`, `endpoint_port`, db name and user.

---

## 2. Terraform Configuration (dev env)

Location: `infra/terraform/envs/dev`.

### 2.1 `variables.tf`

Defined variables:

```hcl
variable "scw_access_key" {
  type      = string
  sensitive = true
}

variable "scw_secret_key" {
  type      = string
  sensitive = true
}

variable "scw_project_id" {
  type      = string
  sensitive = true
}

variable "scw_region" {
  type    = string
  default = "fr-par"
}

variable "mobi_db_password" {
  type      = string
  sensitive = true
}
```

### 2.2 `main.tf` (current key resources)

Relevant blocks (simplified):

```hcl
data "scaleway_account_project" "current" {
  project_id = var.scw_project_id
}

resource "scaleway_vpc_private_network" "dev" {
  name = "mobi-dev-private-network"
  tags = ["env:dev", "app:mobi"]
}

resource "scaleway_k8s_cluster" "dev" {
  name        = "mobi-dev-cluster"
  description = "Dev Kubernetes cluster for mobi"

  type = "kapsule"
  cni  = "cilium"
  tags = ["env:dev", "app:mobi"]

  version            = "1.35.0"
  private_network_id = scaleway_vpc_private_network.dev.id

  delete_additional_resources = true
}

resource "scaleway_k8s_pool" "dev_default" {
  cluster_id = scaleway_k8s_cluster.dev.id
  name       = "dev-pool"

  node_type = "DEV1-M"
  size      = 1
  autoscaling = false
  tags = ["env:dev", "app:mobi"]
}

resource "scaleway_rdb_instance" "dev" {
  name          = "mobi-dev-db"
  engine        = "PostgreSQL-16"
  node_type     = "DB-DEV-S"
  is_ha_cluster = false
  region        = var.scw_region
  tags          = ["env:dev", "app:mobi"]
}

resource "scaleway_rdb_database" "mobi" {
  instance_id = scaleway_rdb_instance.dev.id
  name        = "mobi"
}

resource "scaleway_rdb_user" "mobi" {
  instance_id = scaleway_rdb_instance.dev.id
  name        = "mobi"
  password    = var.mobi_db_password
  is_admin    = false
}

output "project_name" {
  value = data.scaleway_account_project.current.name
}

output "k8s_cluster_id" {
  value = scaleway_k8s_cluster.dev.id
}

output "db_connection_url" {
  value       = "postgresql+psycopg://${scaleway_rdb_user.mobi.name}:${var.mobi_db_password}@${scaleway_rdb_instance.dev.endpoint_ip}:${scaleway_rdb_instance.dev.endpoint_port}/${scaleway_rdb_database.mobi.name}"
  sensitive   = true
  description = "SQLAlchemy-compatible connection URL for the mobi dev DB"
}
```

### 2.3 Terraform Dev Workflow (`.github/workflows/terraform-dev.yml`)

- Triggers: push/PR on `infra/terraform/**`.
- Env wiring:

```yaml
env:
  SCW_ACCESS_KEY: ${{ secrets.SCW_ACCESS_KEY }}
  SCW_SECRET_KEY: ${{ secrets.SCW_SECRET_KEY }}
  SCW_DEFAULT_PROJECT_ID: ${{ secrets.SCW_DEFAULT_PROJECT_ID }}
  SCW_DEFAULT_REGION: ${{ secrets.SCW_DEFAULT_REGION }}
  TF_VAR_scw_access_key: ${{ secrets.SCW_ACCESS_KEY }}
  TF_VAR_scw_secret_key: ${{ secrets.SCW_SECRET_KEY }}
  TF_VAR_scw_project_id: ${{ secrets.SCW_DEFAULT_PROJECT_ID }}
  TF_VAR_scw_region: ${{ secrets.SCW_DEFAULT_REGION }}
  TF_VAR_mobi_db_password: ${{ secrets.MOBI_DB_PASSWORD }}
```

- Steps:
  - Checkout
  - Setup Terraform 1.9.8
  - `terraform init -input=false`
  - `terraform plan -input=false`
  - On push to `main`: `terraform apply -input=false -auto-approve`.

This workflow now fully creates:
- `mobi-dev-private-network`
- `mobi-dev-cluster` + `dev-pool`
- `mobi-dev-db` + `mobi` DB + `mobi` user.

---

## 3. K8s Layer (manifests in `k8s/`)

### 3.1 Namespace

`k8s/namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mobi-dev
```

CI ensures this exists before secrets and app resources.

### 3.2 Backend Deployment & Service (`k8s/backend.yaml`)

#### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mobi-backend
  namespace: mobi-dev
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mobi-backend
  template:
    metadata:
      labels:
        app: mobi-backend
    spec:
      containers:
        - name: mobi-backend
          image: rg.pl-waw.scw.cloud/garganache/mobi-backend:latest
          imagePullPolicy: IfNotPresent
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: mobi-backend-db
                  key: DATABASE_URL
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 30
```

#### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mobi-backend
  namespace: mobi-dev
spec:
  selector:
    app: mobi-backend
  ports:
    - name: http
      port: 8000
      targetPort: 8000
  type: ClusterIP
```

### 3.3 Frontend Deployment & Service (`k8s/frontend.yaml`)

#### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mobi-frontend
  namespace: mobi-dev
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mobi-frontend
  template:
    metadata:
      labels:
        app: mobi-frontend
    spec:
      containers:
        - name: mobi-frontend
          image: rg.pl-waw.scw.cloud/garganache/mobi-frontend:latest
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 80
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 30
            periodSeconds: 30
```

#### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mobi-frontend
  namespace: mobi-dev
spec:
  selector:
    app: mobi-frontend
  ports:
    - name: http
      port: 80
      targetPort: 80
  type: ClusterIP
```

### 3.4 Ingress (App) – `k8s/ingress.yaml`

Currently we use **two** ingress resources to keep `/api` rewrites from affecting static assets:

```yaml
# Backend ingress: /api → backend with regex + rewrite
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mobi-backend-ingress
  namespace: mobi-dev
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/use-regex: "true"
spec:
  ingressClassName: nginx
  rules:
    - http:
        paths:
          - path: /api(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: mobi-backend
                port:
                  number: 8000
---
# Frontend ingress: / → frontend, no rewrite
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mobi-frontend-ingress
  namespace: mobi-dev
spec:
  ingressClassName: nginx
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: mobi-frontend
                port:
                  number: 80
```

Notes:
- `/api/description` from the browser is rewritten to `/description` before hitting FastAPI, matching dev/Vite behavior.
- `/assets/*` and `/` go directly to the frontend service with no rewrite, so JS bundles are served with the right MIME type.

### 3.5 Ingress Controller – `k8s/ingress-nginx.yaml`

- Vendored from:
  - `https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml`
- Deploys in namespace `ingress-nginx`:
  - `ingress-nginx-controller` Deployment
  - `ingress-nginx-controller` Service (type `LoadBalancer`)
  - Admission webhook jobs + RBAC + `IngressClass` named `nginx`.
- External IP of controller service becomes the public IP for the app.

Current observed external IP:
- `151.115.13.108` (as of this snapshot).

---

## 4. Backend Application Details

Location: `backend/app/main.py`.

Key behaviors:

```py
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
  raise RuntimeError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()

class Description(Base):
    __tablename__ = "descriptions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


class DescriptionIn(BaseModel):
    text: str


class DescriptionOut(BaseModel):
    id: int
    text: str
    created_at: datetime

    class Config:
        orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="Mobi Backend")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    """Simple health check for Kubernetes probes."""
    return {"status": "ok"}


@app.post("/description", response_model=DescriptionOut)
def create_description(payload: DescriptionIn, db: Session = Depends(get_db)):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Description cannot be empty")

    desc = Description(text=text)
    db.add(desc)
    db.commit()
    db.refresh(desc)
    return desc


@app.get("/description/latest", response_model=Optional[DescriptionOut])
def get_latest_description(db: Session = Depends(get_db)):
    desc = db.query(Description).order_by(Description.created_at.desc()).first()
    if desc is None:
        raise HTTPException(status_code=404, detail="No description found")
    return desc


@app.get("/description", response_model=list[DescriptionOut])
def list_descriptions(limit: int = 10, db: Session = Depends(get_db)):
    """Return the most recent descriptions, newest first."""
    q = db.query(Description).order_by(Description.created_at.desc()).limit(limit)
    return q.all()
```

Notes:
- DB schema is auto-created on startup via `Base.metadata.create_all`.
- `/health` is used by K8s liveness/readiness probes.
- `/description` supports POST (create) and GET (list recent).
- `/description/latest` returns the most recent entry or 404.

---

## 5. Frontend Application Details

Location: `frontend`.

### 5.1 Build & Runtime

- Build: Vite + Svelte (Svelte 5, using classic `App.svelte` with a Svelte 5-compatible `main.ts`).
- Dev proxy config (`frontend/vite.config.mts`):

```ts
import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
```

- Container image: built from `frontend/Dockerfile`:

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 5.2 App.svelte behavior (`frontend/src/App.svelte`)

Key parts (current):

```svelte
<script lang="ts">
  import { onMount } from 'svelte';

  let text = '';
  let status: string | null = null;
  let loading = false;
  let history: { id: number; text: string; created_at: string }[] = [];

  async function loadLatest() {
    try {
      const res = await fetch('/api/description/latest');
      if (res.ok) {
        const data = await res.json();
        text = data.text;
      }
    } catch (e) {
      console.error('Failed to load latest description', e);
    }
  }

  async function loadHistory() {
    try {
      const res = await fetch('/api/description?limit=10');
      if (res.ok) {
        history = await res.json();
      }
    } catch (e) {
      console.error('Failed to load description history', e);
    }
  }

  async function save() {
    status = null;
    loading = true;
    try {
      const res = await fetch('/api/description', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      if (res.ok) {
        status = 'Saved successfully';
        await loadHistory();
      } else {
        const data = await res.json().catch(() => ({}));
        status = data.detail ?? 'Save failed';
      }
    } catch (e) {
      status = 'Network error';
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadLatest();
    loadHistory();
  });
</script>

<main>
  <h1>Mobi Description</h1>

  <label for="description">Description</label>
  <textarea
    id="description"
    bind:value={text}
    rows="4"
    cols="40"
    placeholder="Type a description..."
  ></textarea>

  <button on:click={save} disabled={loading}>
    {#if loading}
      Saving...
    {:else}
      Save
    {/if}
  </button>

  {#if status}
    <p data-testid="status">{status}</p>
  {/if}

  {#if history.length}
    <section style="margin-top: 2rem;">
      <h2>Recent descriptions</h2>
      <ul>
        {#each history as item}
          <li>{item.text}</li>
        {/each}
      </ul>
    </section>
  {/if}
</main>
```

Notes:
- Frontend always calls `/api/...`; in dev, Vite rewrites to `/...` on the backend; in prod, NGINX ingress does the same via regex + rewrite.

---

## 6. CI/CD – Build and Deploy Workflow

Location: `.github/workflows/build-and-deploy.yml`.

### 6.1 Trigger & Job-level Env

- Trigger: `push` to `main`.

Job env:

```yaml
env:
  REGISTRY: rg.pl-waw.scw.cloud/garganache
  BACKEND_IMAGE: rg.pl-waw.scw.cloud/garganache/mobi-backend
  FRONTEND_IMAGE: rg.pl-waw.scw.cloud/garganache/mobi-frontend
  SCW_K8S_CLUSTER_ID: ${{ secrets.SCW_K8S_CLUSTER_ID }}
  MOBI_DB_URL: ${{ secrets.MOBI_DB_URL }}   # or future derived variant
```

### 6.2 Steps (high level)

1. **Checkout** repo.
2. **Configure Scaleway env** (echo only, actual creds used by `scw`).
3. **Install Scaleway CLI**:

   ```bash
   curl -s https://raw.githubusercontent.com/scaleway/scaleway-cli/master/scripts/get.sh | sudo sh
   scw version
   ```

4. **Configure Scaleway CLI profile** using secrets (`SCW_ACCESS_KEY`, `SCW_SECRET_KEY`, `SCW_DEFAULT_PROJECT_ID`, `SCW_DEFAULT_ORGANIZATION_ID`, `SCW_DEFAULT_REGION`).
5. **Install kubeconfig for cluster** from `SCW_KUBECONFIG_B64` secret:

   ```bash
   mkdir -p ~/.kube
   echo "$SCW_KUBECONFIG_B64" | base64 -d > ~/.kube/config
   ```

6. **Install kubectl** via apt.
7. **Docker login** to Scaleway registry using `SCW_SECRET_KEY`.
8. **Build images**:

   ```bash
   docker build -t $BACKEND_IMAGE:${{ github.sha }} backend
   docker tag  $BACKEND_IMAGE:${{ github.sha }} $BACKEND_IMAGE:latest

   docker build -t $FRONTEND_IMAGE:${{ github.sha }} frontend
   docker tag  $FRONTEND_IMAGE:${{ github.sha }} $FRONTEND_IMAGE:latest
   ```

9. **Push images** (SHA + `latest`).
10. **Install/upgrade ingress-nginx** from `k8s/ingress-nginx.yaml`.
11. **Reset app ingresses**:

    ```bash
    kubectl -n mobi-dev delete ingress mobi-ingress mobi-backend-ingress mobi-frontend-ingress --ignore-not-found=true
    ```

12. **Ensure namespace exists**:

    ```bash
    kubectl apply -f k8s/namespace.yaml
    ```

13. **Ensure backend DB secret exists** (current behavior):

    ```bash
    kubectl -n mobi-dev create secret generic mobi-backend-db \
      --from-literal=DATABASE_URL="${MOBI_DB_URL}" \
      --dry-run=client -o yaml | kubectl apply -f -
    ```

14. **Deploy to Kubernetes**:

    ```bash
    kubectl apply -f k8s/backend.yaml -f k8s/frontend.yaml -f k8s/ingress.yaml

    kubectl -n mobi-dev set image deployment/mobi-backend mobi-backend=$BACKEND_IMAGE:${{ github.sha }}
    kubectl -n mobi-dev set image deployment/mobi-frontend mobi-frontend=$FRONTEND_IMAGE:${{ github.sha }}

    kubectl -n mobi-dev get pods
    kubectl -n mobi-dev get svc
    kubectl -n mobi-dev get ingress -o wide
    ```

Result: every push to `main` will:
- Ensure ingress-nginx is present.
- Ensure namespace + DB secret + app manifests are applied.
- Update backend/frontend deployments to the new image tags.

---

## 7. Runtime State & Behavior (as of this snapshot)

- **Cluster:** `mobi-dev-cluster` exists with one `DEV1-M` node.
- **Namespace:** `mobi-dev` contains:
  - `mobi-backend` Deployment (2 pods), Service, DB secret `mobi-backend-db`.
  - `mobi-frontend` Deployment (2 pods), Service.
  - `mobi-backend-ingress` and `mobi-frontend-ingress` pointing to those services.
- **Ingress controller:**
  - `ingress-nginx-controller` Service has an external IP (e.g. `151.115.13.108`).
- **External entrypoint:**
  - UI: `http://151.115.13.108/`
  - API: `http://151.115.13.108/api/description`, `/api/description/latest`.
- **DB:**
  - Hosted in Scaleway RDB instance `mobi-dev-db`.
  - App connects via `DATABASE_URL` set from `MOBI_DB_URL` → `mobi-backend-db` secret.
  - All backend pods share this DB, so description history is consistent across replicas.

---

This file is meant as a baseline. Future changes (e.g., different node sizes, adding staging/prod envs, switching to Helm, tightening DB roles) should be reflected here so we don’t have to rediscover these details again later.
