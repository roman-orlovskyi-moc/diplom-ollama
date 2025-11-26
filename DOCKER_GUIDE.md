# Docker Deployment Guide

This guide explains how to run the Prompt Injection Testing Framework using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)

### Install Docker on Ubuntu

```bash
# Update package index
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

## Quick Start

### 1. Build and Start Services

```bash
cd /home/master/www/diplom

# Start all services
docker compose up -d

# View logs
docker compose logs -f
```

This will:
- Start Ollama service on port 11434
- Build the application container
- Set up networking between services

### 2. Pull Ollama Models

```bash
# Pull main model (required)
docker compose exec ollama ollama pull llama3.2

# Pull guardian model for DualLLM defense (recommended)
docker compose exec ollama ollama pull llama3.2:1b

# Verify models are downloaded
docker compose exec ollama ollama list
```

**Models:**
- `llama3.2` - Main LLM for processing requests
- `llama3.2:1b` - Guardian model for DualLLM defense

### 3. Setup Database

```bash
# Access application container
docker compose exec app bash

# Inside container:
python scripts/setup_db.py
```

### 4. Run Tests

```bash
# Still inside the container:

# Verify setup
python scripts/test_setup.py

# Run simple test
python scripts/run_simple_test.py

# Run full experiments
python scripts/run_experiments.py

# Generate report
python scripts/generate_report.py

# Exit container
exit
```

## Docker Compose Commands

### Start Services

```bash
# Start in background
docker compose up -d

# Start with logs visible
docker compose up

# Start specific service
docker compose up ollama
```

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (deletes Ollama model!)
docker compose down -v
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f ollama
docker compose logs -f app
```

### Execute Commands

```bash
# Interactive bash shell in app container
docker compose exec app bash

# Run specific command
docker compose exec app python scripts/test_setup.py

# Run command in Ollama container
docker compose exec ollama ollama list
```

### Rebuild Container

```bash
# Rebuild after code changes
docker compose build app

# Rebuild and restart
docker compose up -d --build
```

## Development Mode

For development with hot reload:

```bash
# Use development compose file
docker compose -f docker-compose.dev.yml up -d

# Access shell
docker compose -f docker-compose.dev.yml exec app bash
```

## Data Persistence

### Volumes

The setup uses Docker volumes to persist data:

1. **ollama_data** - Stores Ollama models (survives container restarts)
2. **./data** - Mounted to host (test results, exports)
3. **./logs** - Mounted to host (application logs)

### Access Results on Host

Results are accessible on your host machine:

```bash
# View results
ls -la data/results/
ls -la data/exports/

# Open CSV in spreadsheet
libreoffice data/exports/experiment_results.csv
```

## Environment Variables

Configure via `docker-compose.yml` or create `.env.docker` file:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2
DATABASE_PATH=/app/data/results/test_results.db
LOG_LEVEL=INFO
```

## Using Different LLM Providers

### OpenAI (GPT)

```yaml
# In docker-compose.yml, modify app environment:
environment:
  - LLM_PROVIDER=openai
  - OPENAI_API_KEY=your-api-key-here
  - OPENAI_MODEL=gpt-4
```

### Anthropic (Claude)

```yaml
# In docker-compose.yml, modify app environment:
environment:
  - LLM_PROVIDER=anthropic
  - ANTHROPIC_API_KEY=your-api-key-here
  - ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

## Common Workflows

### Workflow 1: Quick Test

```bash
# Start services
docker compose up -d

# Wait for Ollama to be ready
docker compose exec ollama ollama pull llama3.2

# Run test
docker compose exec app python scripts/run_simple_test.py
```

### Workflow 2: Full Experiment

```bash
# Start services
docker compose up -d

# Setup models
docker compose exec ollama ollama pull llama3.2
docker compose exec ollama ollama pull llama3.2:1b  # For DualLLM defense

# Setup database
docker compose exec app python scripts/setup_db.py

# Run experiments (interactive)
docker compose exec app python scripts/run_experiments.py

# Generate report
docker compose exec app python scripts/generate_report.py

# Check results on host
ls -la data/exports/
```

### Workflow 3: Development

```bash
# Start in development mode
docker compose -f docker-compose.dev.yml up -d

# Work interactively
docker compose -f docker-compose.dev.yml exec app bash

# Inside container, make changes and test
python scripts/run_simple_test.py

# Changes to src/ are immediately reflected (mounted volume)
```

## Troubleshooting

### Ollama Not Ready

```bash
# Check Ollama health
docker compose exec ollama curl http://localhost:11434/api/tags

# View Ollama logs
docker compose logs ollama

# Restart Ollama
docker compose restart ollama
```

### Model Not Downloaded

```bash
# Check available models
docker compose exec ollama ollama list

# Pull model
docker compose exec ollama ollama pull llama3.2

# If stuck, remove and re-pull
docker compose exec ollama ollama rm llama3.2
docker compose exec ollama ollama pull llama3.2
```

### Connection Refused

```bash
# Check if services are running
docker compose ps

# Check network connectivity
docker compose exec app ping ollama

# Check Ollama URL in app
docker compose exec app env | grep OLLAMA
```

### Permission Errors

```bash
# Fix data directory permissions
sudo chown -R $USER:$USER data/ logs/

# Or run container as root (not recommended)
docker compose exec -u root app bash
```

### Container Won't Start

```bash
# View build logs
docker compose build app --no-cache

# Check logs
docker compose logs app

# Remove all containers and rebuild
docker compose down
docker compose up -d --build
```

## Performance Tips

### 1. Use GPU for Ollama (if available)

```yaml
# In docker-compose.yml, add to ollama service:
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 2. Increase Memory Limit

```yaml
# In docker-compose.yml:
services:
  app:
    deploy:
      resources:
        limits:
          memory: 4G
```

### 3. Use Smaller Model

```bash
# Use llama3.2:1b instead of llama3.2 (default is 3b)
docker compose exec ollama ollama pull llama3.2:1b

# Update environment in docker-compose.yml:
environment:
  - OLLAMA_MODEL=llama3.2:1b
```

## Backup and Restore

### Backup Data

```bash
# Backup test results
tar -czf backup_$(date +%Y%m%d).tar.gz data/ logs/

# Backup Ollama models
docker run --rm -v diplom_ollama_data:/data -v $(pwd):/backup ubuntu tar czf /backup/ollama_backup.tar.gz /data
```

### Restore Data

```bash
# Restore test results
tar -xzf backup_20241115.tar.gz

# Restore Ollama models
docker run --rm -v diplom_ollama_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/ollama_backup.tar.gz -C /
```

## Clean Up

### Remove Everything

```bash
# Stop and remove containers, networks
docker compose down

# Remove volumes too (deletes Ollama models!)
docker compose down -v

# Remove images
docker rmi $(docker images -q thesis-*)
```

### Clean Old Data

```bash
# Clear test results
rm -f data/results/*.db

# Clear exports
rm -rf data/exports/*

# Clear logs
rm -f logs/*.log
```

## Production Deployment

For production deployment on a server:

```bash
# 1. Clone repository
git clone <your-repo> /opt/thesis-project
cd /opt/thesis-project

# 2. Start services
docker compose up -d

# 3. Pull models
docker compose exec ollama ollama pull llama3.2
docker compose exec ollama ollama pull llama3.2:1b  # For DualLLM defense

# 4. Setup database
docker compose exec app python scripts/setup_db.py

# 5. Run experiments (can be scheduled)
docker compose exec app python scripts/run_experiments.py

# 6. Generate reports
docker compose exec app python scripts/generate_report.py
```

### Scheduled Experiments (Optional)

Create a cron job to run experiments automatically:

```bash
# Edit crontab
crontab -e

# Add line to run daily at 2 AM
0 2 * * * cd /opt/thesis-project && docker compose exec -T app python scripts/run_experiments.py
```

## Advantages of Docker Setup

1. **Portability**: Run anywhere Docker is available
2. **Isolation**: No conflicts with system packages
3. **Reproducibility**: Same environment every time
4. **Easy Cleanup**: Remove everything with one command
5. **Multiple Instances**: Run different versions in parallel
6. **CI/CD Ready**: Easy to integrate with automation

## Comparison: Docker vs Local

| Aspect | Docker | Local Install |
|--------|--------|---------------|
| Setup Time | 5 minutes | 15-30 minutes |
| Portability | High | Low |
| Isolation | Complete | None |
| Performance | ~5% overhead | Native |
| Cleanup | Easy | Manual |
| Updates | Rebuild image | Manual updates |

## Next Steps

1. Start services: `docker compose up -d`
2. Pull models:
   - `docker compose exec ollama ollama pull llama3.2`
   - `docker compose exec ollama ollama pull llama3.2:1b` (for DualLLM)
3. Run tests: `docker compose exec app python scripts/run_simple_test.py`
4. View results: `ls -la data/exports/`

For more help, see:
- `README.md` - Project overview
- `QUICKSTART.md` - Local installation guide
- `PROJECT_IMPLEMENTATION_GUIDE.md` - Technical details