# Pipecat Maximum Feature Workflow (Master Blueprint)

This document serves as your complete blueprint for a high-feature, production-ready AI agent using Pipecat Cloud, Gemini Multimodal Live, Krisp VIVA Noise Cancellation, Telephony (Twilio/SIP), Automated Session Recording, and a cost-optimized, zero-downtime "Free Fallback" architecture.

---

## 1. Architecture Overview (The Free Fallback Router)

To achieve a resilient, zero-cost production deployment, we implement a multi-tiered failover traffic strategy:

- **Traffic Controller Layer:** Cloudflare (DNS & Load Balancing). Configured with "Active Health Checks" targeting the Primary tier.
- **Primary Tier (Always On / Persistent):** Oracle Cloud Infrastructure (OCI) Free Tier (Up to 4 ARM Ampere A1 cores, 24 GB RAM). Runs the persistent Dockerized agent via **Coolify** (a self-hosted PaaS).
- **Secondary Tier (Failover / Scale-to-Zero):** Railway or Render. Deployed with `min_instances = 0` to preserve free usage. Spins up automatically if the Primary OCI instance health check fails.
- **Frontend Presentation Layer:** Vercel or Netlify. Hosts the Next.js / React / Gradio Voice UI, ensuring 100% uptime for static assets and CDN caching.

```
                  [ User Browser / Web Phone ]
                                │
                                ▼
                      [ Cloudflare DNS Router ]
                                │
             ┌──────────────────┴──────────────────┐
             ▼ (Primary Health Check)              ▼ (Failover)
   [ OCI Free Tier + Coolify ]           [ Railway / Render ]
     (Persistent WebSockets)               (Scale-to-Zero Backup)
```

---

## 2. Core Repositories & Tooling Setup

- **Core Infrastructure:** [pipecat-cloud](https://github.com/daily-co/pipecat-cloud)
- **Starter Kit Template:** [pcc-gemini-screen-voice-ui-kit](https://github.com/daily-co/pcc-gemini-screen-voice-ui-kit)
- **Deployment Action:** [pipecat-cloud-deploy-action](https://github.com/daily-co/pipecat-cloud-deploy-action)

### Global Dependencies Installation
```bash
# 1. Install Pipecat CLI globally
uv tool install "pipecat-ai[cli]" --with pipecatcloud

# 2. Setup project environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3. Configuration Files

### `Dockerfile`
Place this in your project root to handle system dependencies (including FFmpeg for audio/video streams).

```dockerfile
# Use a slim Python image for efficiency
FROM python:3.11-slim

# Install system dependencies required for audio/multimodal processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

EXPOSE 8080

CMD ["python", "main.py"]
```

### `docker-compose.yml`
Optimized for Coolify deployment on OCI Ampere A1 instances.

```yaml
version: "3.8"

services:
  pipecat-agent:
    build:
      context: .
      dockerfile: Dockerfile
    restart: always
    environment:
      - PORT=8080
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - VERTEXAI_PROJECT_ID=${VERTEXAI_PROJECT_ID}
      - VERTEXAI_LOCATION=${VERTEXAI_LOCATION}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    labels:
      - traefik.enable=true
      - traefik.http.routers.agent.rule=Host(`${DOMAIN}`)
```

### `pcc-deploy.toml`
Enables "Batteries-Included" features in Pipecat Cloud deployments.

```toml
[deployment]
name = "my-max-pipecat-agent"
krisp_viva = true        # Integrated Audio Noise Cancellation
telephony = "twilio"     # Twilio / SIP Integration
recording = true         # Automated Session Recording

[scaling]
min_instances = 1
max_instances = 3
```

---

## 4. Gemini Multimodal Integration

Configure these variables in your environment manager (Coolify UI / Railway Dashboard / `.env`):

| Variable | Description |
| :--- | :--- |
| `GOOGLE_API_KEY` | Primary API Key for Google Cloud / Gemini Live API |
| `VERTEXAI_PROJECT_ID` | GCP Project ID for Vertex AI Multimodal resources |
| `VERTEXAI_LOCATION` | Region deployment (e.g., `us-central1`) |
| `MODEL` | Target Gemini Model (e.g., `gemini-2.0-flash-exp`) |
| `OPENAI_API_KEY` | Optional fallback or secondary tools integration |

---

## 5. CI/CD & Frontend Integration (Vercel / Netlify)

### `.github/workflows/deploy.yml`
```yaml
name: Deploy Pipecat Agent
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: daily-co/pipecat-cloud-deploy-action@v1
        with:
          api_key: ${{ secrets.PIPECAT_API_KEY }}
```

### Frontend Integration (Vercel / Netlify)
- **Decoupled Architecture:** Deploy your UI (Next.js / React / Voice UI Kit) to Vercel or Netlify.
- **WebSocket Endpoint:** Connect client API and WebSocket calls directly to your Coolify OCI instance URL (`https://agent.yourdomain.com`).
- **CORS Setup:** Ensure your Pipecat backend explicitly allows cross-origin requests from your Vercel/Netlify domain.

---

## 6. Daily Operational Commands

| Action | Command |
| :--- | :--- |
| **Start Local Dev** | `docker-compose up -d` |
| **Deploy Update** | `git push origin main` *(Triggers CI/CD)* |
| **Test Integration** | `pytest tests/integration -v` |
| **CLI Status** | `pcc status` |
