# Setup Guide

## Required toolchains

- Python 3.12+
- `uv`
- Node.js 22+
- Docker and Docker Compose
- Go 1.23+
- Rust stable toolchain
- Foundry

Hardhat is installed through the package manifest in `demo/contracts/hardhat`.

## Recommended setup sequence

### 1. Clone and configure

```bash
git clone <your-repo-url> specforge-ai
cd specforge-ai
cp .env.example .env
```

### 2. Python platform

```bash
cd platform
uv sync
```

### 3. Hardhat dependencies

```bash
cd ../demo/contracts/hardhat
npm install
```

### 4. Local services

```bash
cd ../../..
docker compose up --build
```

### 5. Optional native tool checks

```bash
go version
cargo --version
forge --version
```

## Local commands

### CLI

```bash
cd platform
uv run specforge ingest ../demo/specs
uv run specforge plan
uv run specforge generate
uv run specforge run
uv run specforge evaluate
uv run specforge report
```

### Dashboard

```bash
cd dashboard
uv run streamlit run app.py
```

### Go API

```bash
cd demo/api-go
go run ./cmd/server
```

### Rust mutator

```bash
cd demo/mutator-rust
cargo run -- --schema ../specs/openapi.yaml --seed cases/basic-orders.json
```

### Solidity tests

```bash
cd demo/contracts
forge test
cd hardhat
npm run smoke
```

## Notes

- The mock LLM provider is the default local mode and does not require API keys.
- Real provider integrations are available through environment configuration and adapter wiring.
- Pinecone is intentionally optional; pgvector is the default retrieval target.

