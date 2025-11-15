# Docker Quick Start - 5 Minutes to Running

The absolute fastest way to get started with the Prompt Injection Testing Framework.

## Prerequisites

- Docker installed on your system
- Internet connection (to download images)

## Super Quick Start

```bash
# 1. Start everything
./docker.sh start

# 2. Initial setup (downloads model, sets up database)
./docker.sh setup

# 3. Run a quick demo
./docker.sh demo

# That's it! You just tested prompt injection attacks with defenses!
```

## What Just Happened?

1. **Docker started 2 containers**:
   - Ollama (local LLM server)
   - Application (your testing framework)

2. **Setup downloaded**:
   - llama3.2 model (~2GB)
   - Created SQLite database
   - Loaded 56 attack patterns

3. **Demo ran**:
   - 1 attack tested against 3 different defenses
   - Results shown in terminal
   - Data saved to database

## Next Steps

### View Results

```bash
# Check what was generated
./docker.sh results

# Or directly look at files
ls -la data/results/
ls -la data/exports/
```

### Run Full Experiments

```bash
# This tests all 56 attacks against all defenses
# Takes ~15-30 minutes
./docker.sh experiment
```

### Generate Thesis Report

```bash
# Creates visualizations and analysis
./docker.sh report

# View outputs
ls -la data/exports/visualizations/
```

### Interactive Exploration

```bash
# Open a shell inside the container
./docker.sh shell

# Now you can run Python directly:
python scripts/test_setup.py
python scripts/run_simple_test.py

# Or use Python interactively:
python
>>> from src.core.attack_engine import AttackEngine
>>> engine = AttackEngine()
>>> engine.load_attacks()
56
>>> exit()

# Exit the container
exit
```

## Common Commands

```bash
./docker.sh start      # Start services
./docker.sh stop       # Stop services
./docker.sh status     # Check if running
./docker.sh logs       # View logs
./docker.sh shell      # Interactive shell
./docker.sh help       # Show all commands
```

## Troubleshooting

### Services Won't Start

```bash
# Check Docker is installed
docker --version

# Check Docker is running
docker ps

# If not running, start Docker daemon
sudo systemctl start docker
```

### Model Download Fails

```bash
# Restart Ollama container
docker compose restart ollama

# Try downloading again
./docker.sh setup
```

### Can't Connect to Ollama

```bash
# Check Ollama is healthy
docker compose exec ollama curl http://localhost:11434/api/tags

# Restart everything
./docker.sh restart
```

## What's Different from Local Install?

| Aspect | Docker | Local |
|--------|--------|-------|
| Installation | One command | Multiple steps |
| Isolation | Complete | None |
| Cleanup | One command | Manual |
| Portability | Run anywhere | System-dependent |
| Updates | Rebuild image | Manual updates |

## File Locations

Everything is stored in your project directory:

- **Database**: `data/results/test_results.db`
- **Exports**: `data/exports/*.csv`, `*.md`, `*.json`
- **Visualizations**: `data/exports/visualizations/*.png`
- **Logs**: `logs/app.log`

These files are on your **host machine**, not inside Docker!

## Complete Workflow (From Zero to Results)

```bash
# 1. Start (30 seconds)
./docker.sh start

# 2. Setup (2-5 minutes, downloads model)
./docker.sh setup

# 3. Quick demo (1 minute)
./docker.sh demo

# 4. Full experiments (15-30 minutes)
./docker.sh experiment

# 5. Generate report (30 seconds)
./docker.sh report

# 6. View results
ls -la data/exports/
cat data/exports/defense_comparison.md
```

## Stopping and Cleanup

```bash
# Stop services (data is preserved)
./docker.sh stop

# Remove everything (including data!)
./docker.sh clean
```

## Tips

1. **First time is slower**: Docker downloads images and Ollama downloads the model
2. **Subsequent runs are fast**: Everything is cached
3. **Data persists**: Even after stopping, your data is safe
4. **Clean slate**: Use `./docker.sh clean` to start fresh

## What to Include in Thesis

After running experiments, you'll have:

1. **data/exports/experiment_results.csv** - All test data
2. **data/exports/defense_comparison.md** - Comparison table
3. **data/exports/summary_statistics.json** - Metrics
4. **data/exports/visualizations/*.png** - Charts

Copy these to your thesis document folder!

## Need More Details?

- **Docker specifics**: See `DOCKER_GUIDE.md`
- **Local install**: See `QUICKSTART.md`
- **Implementation details**: See `PROJECT_IMPLEMENTATION_GUIDE.md`
- **Code examples**: See `USAGE_EXAMPLES.md`

## One-Liner for Impatient People

```bash
./docker.sh start && ./docker.sh setup && ./docker.sh demo && ./docker.sh experiment && ./docker.sh report
```

This does everything from start to finish!

## Advantages of Docker Approach

1. ✅ **No environment conflicts** - Isolated from your system
2. ✅ **Reproducible** - Same environment every time
3. ✅ **Portable** - Works on any system with Docker
4. ✅ **Easy cleanup** - One command removes everything
5. ✅ **Professional** - Industry-standard deployment method

Perfect for demonstrating your thesis project!