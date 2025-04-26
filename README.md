# GENE.ai 🚀



Advanced AI assistant powered by Groq's lightning-fast LLMs with multi-domain knowledge and conversation analytics.

## Features

- Multiple AI personas (Expert, Creative, Technical)
- 7 specialized knowledge domains
- Real-time conversation analytics
- Docker/Kubernetes ready
- CI/CD pipeline
- Responsive UI with dark/light mode

## Repo Structure

nexusai-assistant/
├── .github/
│   ├── workflows/
│   │   └── ci-cd.yml
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── memory.py
│   │   └── utils.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── components.py
│   │   └── layouts.py
│   ├── __init__.py
│   └── main.py
├── configs/
│   ├── __init__.py
│   ├── default.yaml
│   └── production.yaml
├── tests/
│   ├── __init__.py
│   ├── test_chat.py
│   └── test_ui.py
├── docker/
│   ├── nginx.conf
│   └── Dockerfile.prod
├── docs/
│   ├── architecture.md
│   └── setup.md
├── scripts/
│   ├── setup.sh
│   └── deploy.sh
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── README.md
└── LICENSE

## Quick Start

```bash
# Clone repo
git clone https://github.com/wahidpanda/Conversational-Chatbot-with-GROQ-with-Multi-Domain-Expertise-
cd GENE.ai

# Setup environment
cp .env.example .env
# Add your GROQ_API_KEY in .env

# Run with Docker
docker-compose up -d