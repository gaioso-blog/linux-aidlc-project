# CI Pipeline Questions — Task Manager API

## Sources
- [desc] CI definido em `tech-env.md` (GitHub Actions) e implementado em `.github/workflows/ci.yml`
- Upstream: `construction/task-manager-api/code-generation/code-summary.md`, `construction/build-and-test/build-and-test-summary.md`, `construction/build-and-test/build-test-results.md`

## Q1. CI Tool

GitHub Actions foi escolhido no `tech-env.md` e já implementado em `.github/workflows/ci.yml`.

[Answer]: A. GitHub Actions — já implementado e validado

## Q2. Branch Strategy

Trunk-based development (org.md `## Way of Working`): branches de feature curtas, merge para `main` via PR.

[Answer]: A. Trunk-based — branches de feature curtas, merge para main via PR

## Q3. Quality Gates

[Answer]: A. lint (ruff) + format check (black) + pytest ≥85% cobertura — todos já configurados no ci.yml

## Q4. Artifact Repositories

[Answer]: A. S3 para coverage.xml (actions/upload-artifact@v4) — sem ECR ou CodeArtifact na v1

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
