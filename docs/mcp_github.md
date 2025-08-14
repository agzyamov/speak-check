# GitHub MCP Integration

This project is configured to use the GitHub MCP (Model Context Protocol) server for interactions with GitHub (issues, pull requests, projects, and repository contents).

## Prerequisites
- Docker (or Colima with Docker CLI)
- GitHub Personal Access Token (classic) with scopes: `repo`, `read:org` (optionally `project`)

## Setup
1. Add your token to `.env` (not committed):
   ```bash
   echo 'GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx' >> .env
   ```
2. Pull the server image:
   ```bash
   docker pull ghcr.io/github/github-mcp-server:latest
   ```
3. Start the server locally:
   ```bash
   ./scripts/run_github_mcp.sh
   ```
4. Host configuration: see `mcp.config.json` for how the MCP host should launch the server.

## Notes
- Communication is over stdio; your MCP host must spawn the process defined in `mcp.config.json`.
- Keep your token out of git; use `.env` locally.

## Usage
- Once running, all GitHub interactions (list PRs, update issues/PRs, contents, projects) should go through the MCP server.
