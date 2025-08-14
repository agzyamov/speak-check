#!/usr/bin/env bash
set -euo pipefail

# Load .env if present (for local development)
if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [ -z "${GITHUB_PERSONAL_ACCESS_TOKEN:-}" ]; then
  echo "Error: GITHUB_PERSONAL_ACCESS_TOKEN is not set."
  echo "Set it in your environment or in .env, e.g.:"
  echo "  GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx"
  exit 1
fi

echo "Starting GitHub MCP server via Docker..."
exec docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN="${GITHUB_PERSONAL_ACCESS_TOKEN}" \
  ghcr.io/github/github-mcp-server


