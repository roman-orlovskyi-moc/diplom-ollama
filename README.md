# Prompt Injection Testing Framework

Interactive testing framework demonstrating prompt injection attacks and defense mechanisms for Large Language Models.

## Project Overview

This framework implements:
- 50+ documented prompt injection attack patterns
- 5-7 defense mechanisms
- Automated evaluation and metrics
- Web interface for demonstrations
- Comparative analysis data for research

## Quick Start

### Option 1: Docker (Recommended - Easiest)

```bash
# Start services
./docker.sh start

# Setup (pull model, init database)
./docker.sh setup

# Run demo
./docker.sh demo

# Run full experiments
./docker.sh experiment

# Generate report
./docker.sh report
```

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for detailed Docker instructions.

### Option 2: Local Installation

#### 1. Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
```

#### 2. Install Ollama (Free Local LLM)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3.2

# Verify it's running
ollama list
```

#### 3. Initialize Project

```bash
# Set up database
python scripts/setup_db.py

# Verify setup
python scripts/test_setup.py

# Run simple demo
python scripts/run_simple_test.py
```

See [QUICKSTART.md](QUICKSTART.md) for detailed local installation guide.

## Project Structure

```
diplom/
├── config/              # Configuration files
├── data/
│   ├── attacks/         # Attack pattern JSON files
│   ├── results/         # Test results database
│   └── exports/         # Exported metrics and visualizations
├── src/
│   ├── models/          # Data models
│   ├── core/            # Core logic (attack, defense, evaluation)
│   ├── defenses/        # Defense mechanism implementations
│   ├── utils/           # Utility functions
│   └── web/             # Flask web application
├── tests/               # Unit and integration tests
└── scripts/             # Helper scripts
```

## Running Experiments

```bash
# Run full experiment suite
python scripts/run_experiments.py

# Generate report
python scripts/generate_report.py
```

## Defense Mechanisms

1. **Input Sanitization** - Filter dangerous patterns
2. **Prompt Templating** - Structured prompts with delimiters
3. **Output Filtering** - Scan responses for leakage
4. **Dual-LLM Verification** - Guardian model validation
5. **Context Isolation** - Separate instruction and data contexts
6. **Semantic Analysis** - Embedding-based attack detection

## Attack Categories

1. Direct Injection (10+ examples)
2. Jailbreak Attempts (10+ examples)
3. Role Confusion (10+ examples)
4. Context Switching (10+ examples)
5. Indirect Injection (5+ examples)
6. Data Extraction (5+ examples)
