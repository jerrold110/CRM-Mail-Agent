# Exit immediately if a command fails (-e), an undefined variable is used (-u),
# or any command in a pipeline fails (pipefail).
# This avoids continuing with a partially failed Kubernetes deployment.
set -euo pipefail

# Find the repository root regardless of where this script is launched from.
# This script is expected to live at helm/test-local.sh.

ROOT="$PWD"
CHART="$ROOT/helm/application-local"
echo "Chart at $CHART"

# Set defaults for the Kubernetes namespace, Helm release, and existing Secret.
# Each can be overridden by an environment variable when running the script.
NAMESPACE="${NAMESPACE:-portfolio}"
RELEASE="${RELEASE:-portfolio}"
SECRET="${SECRET:-portfolio-app-credentials}"

# Verify that the required command-line tools are installed and accessible.
# Stop early with a clear error instead of failing halfway through deployment.
for cmd in kubectl helm; do
  command -v "$cmd" >/dev/null || { echo "Missing command: $cmd" >&2; exit 1; }
done

# Protect against accidentally deploying to another Kubernetes cluster,
# particularly a future EKS cluster. By default, only Docker Desktop is allowed.
# Set ALLOW_OTHER_CONTEXT=1 explicitly to bypass this safety check.
CONTEXT="$(kubectl config current-context)"
if [[ "$CONTEXT" != 'minikube' && "${ALLOW_OTHER_CONTEXT:-0}" != '1' ]]; then
  echo "Current kubectl context is '$CONTEXT', not 'minikube'." >&2
  echo "To avoid accidental EKS deployment, select minikube or explicitly set ALLOW_OTHER_CONTEXT=1." >&2
  exit 1
fi

# Ensure the target namespace exists.
# --dry-run=client generates the namespace YAML without creating anything;
# piping it into kubectl apply creates it if missing or retains it if present.
# This makes the command safe to execute repeatedly.
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Create secrets from .env file
# kubectl -n portfolio create secret generic \
#   portfolio-app-credentials \
#   --from-env-file=.env

# The Celery worker reads its API keys / Langfuse settings from a Kubernetes
# Secret. Confirm that the Secret already exists in the deployment namespace.
# The script deliberately does not create it or print sensitive values.
if ! kubectl -n "$NAMESPACE" get secret "$SECRET" >/dev/null 2>&1; then
  cat >&2 <<EOF2
Missing Kubernetes Secret '$SECRET' in namespace '$NAMESPACE'.
Create it from your repo-root .env file, e.g.:
  kubectl -n "$NAMESPACE" create secret generic "$SECRET" --from-env-file=.env
Required keys: OPENAI_API_KEY LANGFUSE_SECRET_KEY LANGFUSE_PUBLIC_KEY LANGFUSE_BASE_URL
EOF2
  exit 1
fi

# Check the Helm chart for common errors and validate that local overrides
# in values-local.yaml can be loaded successfully.
helm lint "$CHART" -f "$CHART/values-local.yaml"

# Render Helm templates into Kubernetes YAML without installing anything.
# Sending output to /dev/null keeps the terminal tidy while still failing
# immediately if Helm cannot render the manifests.
helm template "$RELEASE" "$CHART" --namespace "$NAMESPACE" -f "$CHART/values-local.yaml" >/dev/null

# Install the chart if the release does not exist, otherwise upgrade it.
# --wait waits for supported Kubernetes resources to become ready;
# --wait-for-jobs also waits for the one-time database_setup Job to complete.
# --timeout 12m caps how long Helm waits before reporting failure.
# Note: this does NOT build local Docker images; run build-local-images.sh first.
helm upgrade --install "$RELEASE" "$CHART" \
  -n "$NAMESPACE" \
  -f "$CHART/values-local.yaml" \
  --wait --wait-for-jobs --timeout 12m

# Display Pods, Services, and Jobs so you can inspect their current status.
# In particular, database_setup should eventually show as Completed.
kubectl -n "$NAMESPACE" get pods,svc,job

# Print optional commands to access the internal Services from your laptop.
# Port-forwarding is not started here: run each command separately, as shown.
# The curl request checks that FastAPI serves its OpenAPI JSON endpoint.
cat <<EOF2

To open local ports (two terminals):
  kubectl -n "$NAMESPACE" port-forward svc/$RELEASE-api-rest 8000:8000
  kubectl -n "$NAMESPACE" port-forward svc/$RELEASE-redis-commander 8081:8081

Test the API:
  curl -fsS http://127.0.0.1:8000/openapi.json

Check chart installation progress:
  kubectl get pods -n portfolio -w

Check logs of the celery worker deployment:
  kubectl -n portfolio logs deployment/portfolio-celery-worker --all-pods=True -f

EOF2

############
