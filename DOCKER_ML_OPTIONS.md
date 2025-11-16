# Docker ML Defense Options

## Current Situation

Your Docker setup works, but ML defenses will be **slow on first use** because:
1. Models download on first request (~600MB total)
2. Takes 2-5 minutes for first test
3. Not ideal for live demos

## Three Options for Docker + ML

### Option 1: Don't Install ML (Simplest) ✅ RECOMMENDED

**What**: Skip ML dependencies entirely in Docker
**Pros**: Fast build, small image, 6 defenses still work
**Cons**: No ML defenses (PerplexityFilter, SemanticSimilarity)

**How**: Create separate requirements file

**Implementation**: Already done! See below.

---

### Option 2: Install ML, Download Models on First Use ⚠️

**What**: Install ML libs but download models when first used
**Pros**: Full 8 defenses available
**Cons**: First test takes 2-5 minutes, larger Docker image (~4GB)

**How**: Current setup with updated requirements.txt already does this

**Good for**: Testing everything, not for live demos

---

### Option 3: Pre-load ML Models in Docker ⭐ BEST FOR DEMOS

**What**: Download models during Docker build
**Pros**: Instant startup for demos, all 8 defenses ready
**Cons**: Very large image (~5-6GB), slow initial build (~10-15 min)

**How**: See updated Dockerfile below

**Good for**: Live demonstrations, thesis defense presentations

---

## Recommended Approach

### For Development & Experiments: Option 1 or 2

You don't really need ML defenses in Docker for experiments. Use:
- **Docker**: Run experiments with 6 defenses (fast, reliable)
- **Local (venv)**: Install ML libs and test ML defenses when needed

### For Thesis Demo: Option 3

If you need to demonstrate ALL 8 defenses working instantly:
- Pre-load models in Docker image
- Ready for live presentation
- No waiting during demo

---

## Implementation

### Option 1: Skip ML in Docker (RECOMMENDED)

Create `requirements-docker.txt` (without ML):

```txt
# requirements-docker.txt - Lighter version for Docker

# Web Framework
Flask==3.0.0
Flask-CORS==4.0.0

# LLM Clients
openai==1.12.0
anthropic==0.18.0
requests==2.31.0

# Data Processing
pandas==2.1.4
numpy==1.26.3

# Visualization
matplotlib==3.8.2
plotly==5.18.0

# Database
sqlalchemy==2.0.25

# Testing
pytest==7.4.4
pytest-cov==4.1.0

# Utilities
python-dotenv==1.0.0
tqdm==4.66.1

# Code Quality
black==24.1.1
flake8==7.0.0
```

Update `Dockerfile`:
```dockerfile
# Use lighter requirements for Docker
COPY requirements-docker.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
```

**Result**:
- Build time: ~2 minutes
- Image size: ~1GB
- Defenses: 6 (all non-ML + InstructionHierarchy)
- Perfect for experiments

---

### Option 2: ML Without Pre-loading (CURRENT SETUP)

Keep current `requirements.txt` with ML dependencies.

**Already done!** Your current setup is this option.

**Usage**:
```bash
docker compose build
docker compose up
# First ML defense test: 2-5 minutes (downloads models)
# Subsequent tests: Fast
```

**Result**:
- Build time: ~5 minutes
- Image size: ~3-4GB
- Defenses: 8 (but slow first use)

---

### Option 3: Pre-load ML Models (FOR DEMOS)

Create `Dockerfile.ml-preload`:

```dockerfile
# Dockerfile.ml-preload - With pre-loaded ML models
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download ML models (this is the key part!)
RUN python -c "from transformers import GPT2LMHeadModel, GPT2Tokenizer; \
    print('Downloading GPT-2 for perplexity...'); \
    GPT2Tokenizer.from_pretrained('gpt2'); \
    GPT2LMHeadModel.from_pretrained('gpt2'); \
    print('✓ GPT-2 downloaded')"

RUN python -c "from sentence_transformers import SentenceTransformer; \
    print('Downloading sentence transformer...'); \
    SentenceTransformer('all-MiniLM-L6-v2'); \
    print('✓ Sentence transformer downloaded')"

# Copy project files
COPY . .

# Create directories
RUN mkdir -p data/results data/exports/visualizations logs

# Environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "src/app.py"]
```

Create `docker-compose.ml.yml`:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    restart: unless-stopped

  app:
    build:
      context: .
      dockerfile: Dockerfile.ml-preload  # Use ML-preload version
    container_name: app-ml
    depends_on:
      ollama:
        condition: service_healthy
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./src:/app/src
      - ./scripts:/app/scripts
    environment:
      - LLM_PROVIDER=ollama
      - OLLAMA_BASE_URL=http://ollama:11434
      - OLLAMA_MODEL=llama3.2
      - DATABASE_PATH=/app/data/results/test_results.db
      - FLASK_ENV=development
    command: python src/app.py
    restart: unless-stopped

volumes:
  ollama_data:
```

**Usage**:
```bash
# Build (takes ~10-15 min, downloads models)
docker compose -f docker-compose.ml.yml build

# Run
docker compose -f docker-compose.ml.yml up

# Now ALL defenses work instantly!
```

**Result**:
- Build time: ~10-15 minutes (one time)
- Image size: ~5-6GB
- Defenses: 8 (all ready instantly)
- Perfect for demos

---

## My Recommendation

**For your thesis, use a hybrid approach**:

### During Development (Now)
```bash
# Use current Docker for experiments (Option 2)
docker compose up

# For ML defense testing, use local venv
source venv/bin/activate
pip install transformers torch sentence-transformers
python scripts/test_new_features.py
```

### Before Thesis Demo/Defense (Later)
```bash
# Build ML-preload version for presentation
docker compose -f docker-compose.ml.yml build

# Start for demo (everything instant)
docker compose -f docker-compose.ml.yml up
```

---

## Comparison Table

| Aspect | Option 1 (No ML) | Option 2 (ML, No Preload) | Option 3 (ML Preload) |
|--------|------------------|---------------------------|----------------------|
| Build Time | ~2 min | ~5 min | ~10-15 min |
| Image Size | ~1GB | ~3-4GB | ~5-6GB |
| First Use | Instant | 2-5 min wait | Instant |
| Defenses | 6 | 8 | 8 |
| Best For | Experiments | Testing | Live demos |
| Complexity | Simple | Medium | Medium |

---

## What to Do Now

### Immediate (Keep It Simple)

**Don't change anything!** Your current setup (Option 2) works fine for development.

When you run experiments:
- Use Docker for most tests (6 defenses)
- Use local venv when you specifically want to test ML defenses

### Before Thesis Defense (If Needed)

If you need to demonstrate ML defenses in a live presentation:

1. Create `Dockerfile.ml-preload` (see Option 3 above)
2. Create `docker-compose.ml.yml` (see Option 3 above)
3. Build it once: `docker compose -f docker-compose.ml.yml build`
4. Use for demo: `docker compose -f docker-compose.ml.yml up`

---

## Files to Create (Optional)

If you want Option 1 (lightweight Docker):
```bash
# Create requirements-docker.txt (without ML)
# Modify Dockerfile to use requirements-docker.txt
```

If you want Option 3 (demo-ready):
```bash
# Create Dockerfile.ml-preload (with model downloads)
# Create docker-compose.ml.yml (uses new Dockerfile)
```

Both are **optional** - your current setup works!

---

## Summary

✅ **Current setup is fine for now** (Option 2)
- Builds successfully with updated requirements.txt
- Has ML dependencies available
- Downloads models on first use

⚡ **For experiments**: Consider Option 1 (lighter, faster)
- Create requirements-docker.txt without ML
- Faster builds, smaller images
- Use local venv for ML testing

🎯 **For thesis demo**: Consider Option 3 (pre-loaded)
- Create Dockerfile.ml-preload
- Models ready instantly for presentation
- Build once, use for demo day

**My advice**: Stick with current setup for now, only create Option 3 files if you need instant ML demos later.