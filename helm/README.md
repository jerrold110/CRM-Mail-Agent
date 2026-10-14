# Helm chart for the local Docker Desktop Kubernetes cluster

Place this `helm/` directory at the repository root, next to `src/`,
`docker-compose.yml`, `pyproject.toml`, and `uv.lock`. It deploys all seven
existing Compose services. No Dockerfiles or application source files are
modified. No container registry (including ECR) is needed for this local test.

## Layout

```text
helm/
├── application-local/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-local.yaml
│   └── templates/
│       ├── api-deployment.yaml
│       ├── api-service.yaml
│       ├── celery-deployment.yaml
│       ├── database-setup-job.yaml
│       ├── pgbouncer-deployment.yaml
│       ├── pgbouncer-service.yaml
│       ├── postgres-statefulset.yaml
│       ├── postgres-service.yaml
│       ├── redis-deployment.yaml
│       ├── redis-service.yaml
│       ├── redis-commander-deployment.yaml
│       ├── redis-commander-service.yaml
│       └── NOTES.txt
├── build-local-images.sh
├── test-local.sh
└── README.md
```

There is deliberately **no `_helpers.tpl`**. Resource names are simply
`{{ .Release.Name }}-SERVICE` and each Service/Deployment/StatefulSet uses a
single `app: RELEASE-SERVICE` label to connect selectors to Pods.

## 1. Use Docker Desktop Kubernetes

Enable Kubernetes in Docker Desktop, and preferably use its single-node
`kubeadm` cluster to use images built in the Docker Desktop image store.
Check your environment:

```bash
kubectl config use-context docker-desktop
kubectl get nodes
helm version
```

If Docker Desktop uses a **kind-based cluster**, building an image with Docker
does not necessarily make it available to Kubernetes. You may need to load the
local images into the Kubernetes node. The Helm values set
`imagePullPolicy: Never` so Kubernetes will not pull from a registry.

## 2. Build all seven Docker images

Run **from the repository root**:

```bash
docker compose down
bash helm/build-local-images.sh
docker image ls | grep portfolio/
```

Every build uses the Dockerfile *inside its own service directory* (`-f`). The
script accepts both `Dockerfile` and `dockerfile` spelling. The positional
build context intentionally varies to match your existing Compose file:

| Dockerfile | Build context | Image |
|---|---|---|
| `src/databaseSql/Dockerfile` | `./src/databaseSql` | `portfolio/internal-database-sql:local` |
| `src/DBmemorysetup/Dockerfile` | `.` | `portfolio/database-setup:local` |
| `src/pgbouncer/Dockerfile` | `./src/pgbouncer` | `portfolio/pgbouncer:local` |
| `src/redis/Dockerfile` | `./src/redis` | `portfolio/redis-broker:local` |
| `src/redisCommander/Dockerfile` | `./src/redisCommander` | `portfolio/redis-commander:local` |
| `src/api_rest/Dockerfile` | `.` | `portfolio/api-rest:local` |
| `src/agent/Dockerfile` | `.` | `portfolio/celery-worker:local` |

The root context (`.`) is required for Python Dockerfiles that reference
root-level `pyproject.toml`, `uv.lock`, or shared code; using the service folder
as context for those Dockerfiles would break `COPY`. The smaller service
contexts are kept where the working Compose file already uses them (e.g.
Postgres's `COPY init-db.sql /docker-entrypoint-initdb.d/`).

If you later change a Dockerfile's `COPY` sources, update its build context in
`build-local-images.sh` accordingly.

## 3. Create the Celery Kubernetes Secret

Keep the credentials in your existing repo-root `.env` (do not commit it):

```dotenv
OPENAI_API_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_BASE_URL=...
```

```bash
kubectl create namespace portfolio --dry-run=client -o yaml | kubectl apply -f -
kubectl -n portfolio create secret generic portfolio-app-credentials --from-env-file=.env
```

The PostgreSQL demo credentials (`admin` / `admin`) remain ordinary Pod
environment variables as requested. Langfuse URL and public key are stored
alongside the sensitive keys for a 1:1 migration, although they are not
usually secret themselves.

## 4. Render, install, and test

```bash
helm lint ./helm/application -f ./helm/application/values-local.yaml
helm template portfolio ./helm/application -n portfolio -f ./helm/application/values-local.yaml > /tmp/portfolio-rendered.yaml
bash helm/test-local.sh
```

Inspect the workloads:

```bash
kubectl -n portfolio get pods,svc,job
kubectl -n portfolio logs job/portfolio-database-setup
```

For local access, run these in **separate terminals**:

```bash
kubectl -n portfolio port-forward svc/portfolio-api-rest 8000:8000
kubectl -n portfolio port-forward svc/portfolio-redis-commander 8081:8081
```

Visit `http://127.0.0.1:8000/docs` (API) and `http://127.0.0.1:8081`
(Redis Commander). PostgreSQL and PgBouncer are intentionally not exposed on
the host; you can port-forward them for debugging if necessary.

## Health checks and dependency ordering

The healthcheck **commands and settings are retained from Compose**.
Kubernetes uses the same commands in `readinessProbe` with
`initialDelaySeconds` approximating Compose's `start_period`. Exact start
period semantics differ: readiness probes only determine whether the Pod
receives traffic; they do not restart a container after repeated failures.

| Container | Same check as Compose | Initial delay | Interval | Timeout | Failure threshold |
|---|---|---:|---:|---:|---:|
| PostgreSQL | `PGPASSWORD=... psql ... SELECT 1 \| grep -qx '1'` | 30s | 20s | 5s | 10 |
| PgBouncer | `psql` through `127.0.0.1:6432` for **both** databases | 15s | 20s | 5s | 10 |
| Redis broker | `redis-cli ping` | 10s | 5s | 5s | 10 |
| API | `python -c '...urllib.request.urlopen(.../openapi.json, timeout=3)...'` | 15s | 20s | 5s | 10 |
| Redis Commander | No Compose healthcheck | — | — | — | — |
| Celery worker | No Compose healthcheck | — | — | — | — |
| Database setup Job | No Compose healthcheck | — | — | — | — |

`initContainers` stand in for Compose's `depends_on` behavior:

1. PostgreSQL runs the existing `init-db.sql` from its existing Docker image.
2. The one-time database setup Job waits for PostgreSQL, then runs the image's
   existing default command to create the LangGraph memory database.
3. PgBouncer waits for both `company` and `agent_memory` to be accessible;
   its readiness probe then executes your original two-database SQL check.
4. API waits for Redis and PgBouncer readiness via their Kubernetes Services.
5. Celery waits for Redis, PgBouncer, and the API endpoint. Redis Commander
   waits for Redis.

## Rolling updates

All long-running workloads explicitly use `RollingUpdate`:

- API, Celery, PgBouncer, Redis Commander use `maxSurge: 1` and
  `maxUnavailable: 0`.
- **Redis** uses `maxSurge: 0`, `maxUnavailable: 1` to prevent Kubernetes from
  temporarily running **two independent Redis brokers** behind the same
  Service. It will briefly be unavailable on a single replica during updates.
- **PostgreSQL** uses StatefulSet `updateStrategy: RollingUpdate`. With one
  replica and no persistent storage, updates mean downtime and data loss.

RollingUpdate is an update *strategy*, not a guarantee of zero downtime for
single-instance stateful applications.

## Disposable PostgreSQL and setup-Job lifecycle

PostgreSQL remains a **one-replica StatefulSet with no PersistentVolumeClaim**.
The `volumeMounts` and `volumeClaimTemplates` examples are commented out.
That means the database can be lost on Pod replacement or container restart.
The database Dockerfile's SQL bootstrap is unchanged.

An important consequence: a *completed* database setup Job will **not** rerun
just because PostgreSQL was recreated. For a clean local reset, uninstall the
whole Helm release and reinstall, while keeping the namespace and Secret:

```bash
helm uninstall portfolio -n portfolio
bash helm/test-local.sh
```

Do not use this non-persistent setup for important data or production workloads.

## Troubleshooting

```bash
kubectl -n portfolio get pods,svc,job
kubectl -n portfolio get events --sort-by=.lastTimestamp
kubectl -n portfolio logs job/portfolio-database-setup -c database-setup
kubectl -n portfolio logs statefulset/portfolio-internal-database-sql
kubectl -n portfolio logs deploy/portfolio-pgbouncer -c pgbouncer
kubectl -n portfolio logs deploy/portfolio-celery-worker -c celery-worker
```

- `ErrImageNeverPull`: the Kubernetes node doesn't have your local image.
- `CreateContainerConfigError`: check the Secret name, namespace, and four keys.
- PgBouncer init-container blocked: see database setup Job, especially whether
  `agent_memory` was created.
- Celery init-container blocked: inspect Redis, PgBouncer, and API readiness.
- Rebuilding an image with the same `:local` tag does **not** automatically
  roll an existing Deployment. Use `kubectl rollout restart` for the affected
  Deployment, or uninstall/reinstall for a complete ephemeral database reset.

When moving to EKS later: switch images to ECR registry URLs, adjust pull
policy, add the needed cloud identity/secret setup, and retain the Helm chart.
