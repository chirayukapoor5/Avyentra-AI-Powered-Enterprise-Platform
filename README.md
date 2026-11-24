# Avyentra AI Platform

Production-oriented retrieval-augmented generation (RAG) portfolio adaptation.

[![CI workflow](https://github.com/chirayukapoor5/Avyentra-AI-Powered-Enterprise-Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/chirayukapoor5/Avyentra-AI-Powered-Enterprise-Platform/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-container-2496ED?logo=docker)

## Project provenance and contribution scope

Avyentra is a repository maintained under [chirayukapoor5](https://github.com/chirayukapoor5), with branding and documentation changes to the [Enterprise AI Platform repository by aramradif](https://github.com/aramradif/Enterprise-AI-Platform). Credit for the upstream implementation belongs to its original contributors.

The initial import includes the RAG application, frontend, Docker configuration, CI/CD workflow and health test. A source comparison found identical Git blobs for `main.py`, `app/services/rag_service.py`, `frontend/js/api.js`, `Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml` and `tests/test_health.py`. Repository ownership and an import commit do not establish original implementation authorship.

Documented repository-specific changes include branding and README updates. See the [commit history](https://github.com/chirayukapoor5/Avyentra-AI-Powered-Enterprise-Platform/commits/main/) for the actual change record. Additional engineering contributions should be assessed from their individual diffs and test evidence, not attributed to the maintainer solely because they appear in this repository.

## What the inherited implementation demonstrates

- FastAPI REST endpoints for retrieval, streaming, sessions and request logs.
- Hybrid semantic and keyword retrieval with ChromaDB and OpenAI embeddings.
- GPT-4o-mini integration, conversation memory and source citations.
- Evaluation and observability fields for latency, token counts and estimated costs.
- HTML/CSS/JavaScript frontend and local API integration.
- Docker and Docker Compose configuration.
- A GitHub Actions workflow for syntax checks, application import, pytest, image build and a conditional Render deployment hook.

These are features of the codebase, not a claim that the Avyentra maintainer independently authored or operated all of them.

## Architecture

The inherited architecture separates the web client, FastAPI endpoints, RAG orchestration, retrieval, conversation management and logging. See the [upstream repository](https://github.com/aramradif/Enterprise-AI-Platform) for its original diagrams and screenshots.

```text
Web client -> FastAPI -> RAG service -> Hybrid retrieval -> ChromaDB
                            |               |
                            |               +-> Retrieved context
                            +-> Conversation memory -> OpenAI
                            +-> Evaluation / request logs
```

## Run locally

Python 3.12 matches the checked-in Dockerfile and CI configuration.

```bash
git clone https://github.com/chirayukapoor5/Avyentra-AI-Powered-Enterprise-Platform.git
cd Avyentra-AI-Powered-Enterprise-Platform
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and supply your own required configuration, including an OpenAI API key for provider-backed functionality. Do not commit credentials. Then run:

```bash
uvicorn main:app --reload
```

Local endpoints: [Swagger UI](http://127.0.0.1:8000/docs) and [health](http://127.0.0.1:8000/health). The frontend is configured for the local API at port 8000 and can be served separately from the repository root (for example, using VS Code Live Server).

Docker build:

```bash
docker build -t avyentra:local .
docker run --rm --env-file .env -p 8000:8000 avyentra:local
```

## Verification and deployment status

| Item | Evidence / status |
| --- | --- |
| CI configuration | [Repository workflow](.github/workflows/ci.yml) |
| Automated test | [Health endpoint test](tests/test_health.py) |
| CI execution | [This repository's workflow runs](https://github.com/chirayukapoor5/Avyentra-AI-Powered-Enterprise-Platform/actions/workflows/ci.yml); successful execution not independently established in the documentation audit |
| Docker runtime | [Dockerfile](Dockerfile); build/run not independently verified in the documentation audit |
| Render deployment | Conditional deployment hook configured; credentials, service ownership and successful deployment not verified |
| Public demo | No independently verified Avyentra-owned deployment currently documented |

Run the checked-in automated test suite locally:

```bash
python -m compileall app main.py
python -m pytest tests -q
```

The workflow uses Python 3.12 and attempts tests and a Docker build before calling a Render deployment hook on pushes to main. It requires repository-specific configuration and secrets. A configured hook does not establish a successful deployment or a production-grade operating environment.

The Render URL previously listed in this README also appears in the upstream README. It is not presented as an Avyentra-owned service. No third-party endpoint, CI run, screenshot or benchmark is evidence of independent Avyentra deployment.

## Repository-specific engineering extension: offline RAG release gate

This AI-assisted extension adds a dependency-free evaluator, strict input validation, retrieval recall@k, answer phrase checks, latency thresholds, JSON reports, and nonzero exit codes for regressions. It includes 12 unit tests and a dedicated CI workflow with passing and intentionally failing synthetic fixtures.

- [Engineering design and reproduction guide](docs/RAG-QUALITY-GATE.md)
- [Evaluator implementation](quality_gate.py)
- [Unit tests](quality_tests/test_quality_gate.py)
- [Dedicated quality-gate workflow](.github/workflows/rag-quality.yml)

The fixtures test gate behavior, not real RAG quality or production latency. CI execution and deployment integration must be established separately.

## Next engineering milestones (not completed)

- Confirm upstream licensing and permissions.
- Add original, independently reviewable engineering changes with unit and integration tests.
- Establish successful CI runs within this repository.
- Configure an independently controlled deployment with post-deployment smoke tests.
- Document measured reliability and performance, including test environment and limitations.

## License and attribution

The upstream README describes the project as MIT-licensed, but no standalone LICENSE, LICENSE.md or LICENSE.txt was located in either repository during the documentation audit. The previous MIT badge is therefore not used as independent confirmation of licensing. Confirm the applicable license and preserve any required copyright and permission notices before further redistribution or deployment. This README does not grant new rights over upstream code.

Upstream project: [aramradif/Enterprise-AI-Platform](https://github.com/aramradif/Enterprise-AI-Platform).
