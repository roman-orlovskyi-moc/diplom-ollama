# Docker Deployment Guide

This guide explains how to run the Prompt Injection Testing Framework using Docker and Docker Compose.

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

# Run tests
python scripts/run_multi_model_comparison.py

# Generate report
python scripts/generate_report.py
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
docker compose exec app python scripts/run_multi_model_comparison.py

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
```

## Common Workflows

### Workflow 1: Quick Test

```bash
# Start services
docker compose up -d

# Wait for Ollama to be ready
docker compose exec ollama ollama pull llama3.2

# Run test
docker compose exec app python scripts/run_multi_model_comparison.py
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

# Run experiments
docker compose exec app python scripts/run_multi_model_comparison.py

# Generate report
docker compose exec app python scripts/generate_report.py

# Check results on host
ls -la data/exports/
```

## Troubleshooting

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
docker rmi $(docker images -q current-project-*)
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
