#!/bin/sh
set -eu

POSTGRES_HOST="${POSTGRES_HOST:-db}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-ira_municipal}"
POSTGRES_USER="${POSTGRES_USER:-ira_user}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-ira_pass}"

echo "Starting backend app..."
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
