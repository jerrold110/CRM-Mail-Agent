#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Each service has its own Dockerfile. Match the contexts in docker-compose.yml:
# - root context for Python images that COPY pyproject.toml and uv.lock
# - service context for Dockerfiles that COPY paths relative to that service
# - loads image into minikube
build_image() {
    local service="$1" image="$2" context="$3" dockerfile

    if [[ -f "src/$service/Dockerfile" ]]; then
        dockerfile="src/$service/Dockerfile"
    elif [[ -f "src/$service/dockerfile" ]]; then
        dockerfile="src/$service/dockerfile"
    else
        echo "Dockerfile not found for $service (expected src/$service/Dockerfile)" >&2
        return 1
    fi

    echo "Building $image from $dockerfile (context: $context)"
    if ! docker build -f "$dockerfile" -t "$image" "$context"; then
        echo "Docker build failed for $service" >&2
        return 1
    fi
    # Load into minikube
    echo "Loading $image into Minikube"
    if ! minikube image load "$image"; then
        echo "Failed to load $image into Minikube" >&2
        return 1
    fi
}

build_image databaseSql    portfolio/internal-database-sql:local ./src/databaseSql
build_image DBmemorysetup  portfolio/database-setup:local        .
build_image pgbouncer      portfolio/pgbouncer:local            ./src/pgbouncer
build_image redis          portfolio/redis-broker:local         ./src/redis
build_image redisCommander portfolio/redis-commander:local      ./src/redisCommander
build_image api_rest       portfolio/api-rest:local            .
build_image agent          portfolio/celery-worker:local       .

echo 'All 7 local images built; check docker image ls for portfolio/.'
echo 'The Docker Desktop Kubernetes node must be able to access the images.'

build_image() {
    local service="$1" image="$2" context="$3" dockerfile

    if [[ -f "src/$service/Dockerfile" ]]; then
        dockerfile="src/$service/Dockerfile"
    elif [[ -f "src/$service/dockerfile" ]]; then
        dockerfile="src/$service/dockerfile"
    else
        echo "Dockerfile not found for $service (expected src/$service/Dockerfile)" >&2
        return 1
    fi

    echo "Building $image from $dockerfile (context: $context)"
    if ! docker build -f "$dockerfile" -t "$image" "$context"; then
        echo "Docker build failed for $service" >&2
        return 1
    fi

    echo "Loading $image into Minikube"
    if ! minikube image load "$image"; then
        echo "Failed to load $image into Minikube" >&2
        return 1
    fi
}