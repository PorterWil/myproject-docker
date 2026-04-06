#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/$USER/myproject-docker"
BRANCH="main"
LOG_FILE="/home/$USER/myproject-docker/deploy.log"
HEALTH_URL="http://127.0.0.1:8080/health"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== DEPLOY START ==="

cd "$PROJECT_DIR"

log "Checking branch..."
git checkout "$BRANCH"

log "Fetching latest changes..."
git fetch origin

LOCAL_COMMIT="$(git rev-parse HEAD)"
REMOTE_COMMIT="$(git rev-parse origin/$BRANCH)"

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
  log "No new commits. Exiting."
  exit 0
fi

log "Pulling latest code..."
git pull origin "$BRANCH"

log "Rebuilding containers..."
docker compose up -d --build

log "Waiting for app to start..."
sleep 8

log "Running health check..."
if curl -fsS "$HEALTH_URL" > /dev/null; then
  log "Health check passed."
  log "=== DEPLOY SUCCESS ==="
  exit 0
else
  log "Health check failed!"
  log "=== DEPLOY FAILED ==="
  exit 1
fi
