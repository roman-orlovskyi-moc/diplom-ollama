# Next Steps - Quick Reference Guide

**Status**: ✅ Implementation Complete!

**You now have**:
- 84 total attacks (added 18 new attacks)
- 8 defense mechanisms (added 3 new defenses)
- 2 new attack categories: Adversarial Techniques & Multi-Turn
- 3 new defenses: InstructionHierarchy, PerplexityFilter, SemanticSimilarity

**Everything is tested and working!**

---

## Quick Start Options

### Option 1: Quick Start (No ML) - 1 hour ⚡

Perfect if you want data immediately without installing ML libraries.

```bash
cd /home/master/www/diplom
source venv/bin/activate
python scripts/run_experiments.py
python scripts/generate_report.py
```

- Tests: 84 attacks × 6 defenses = 504 tests
- Time: ~45-60 minutes
- Cost: Free (uses Ollama)
- Output: `data/exports/`

### Option 2: Full Suite with ML (Recommended) - 2-3 hours 🎯

Complete data with all 8 defenses.

```bash
# Install ML dependencies
source venv/bin/activate
pip install transformers torch sentence-transformers

# Run experiments
python scripts/run_experiments.py
python scripts/generate_report.py
```

- Tests: 84 attacks × 8 defenses = 672 tests
- Time: ~2-3 hours
- Cost: Free
- Output: `data/exports/`

### Option 3: Use GPT-4 (Best Quality) - 30-60 min + $10-15 💎

Highest quality results for thesis.

```bash
# Get API key from https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-..."

# Edit config/settings.py:
# DEFAULT_LLM_PROVIDER = "openai"
# DEFAULT_MODEL = "gpt-4o-mini"

# Run experiments
python scripts/run_experiments.py
python scripts/generate_report.py
```

- Tests: 672 tests
- Time: ~20-30 minutes
- Cost: ~$10-15
- Quality: Best

---

## Quick Commands

```bash
# Test everything works
python scripts/test_new_features.py

# Quick demo
python scripts/run_simple_test.py

# Full experiments
python scripts/run_experiments.py

# Generate report
python scripts/generate_report.py

# Check results
sqlite3 data/results/test_results.db "SELECT COUNT(*) FROM test_results;"
```

---

## What You'll Get

**Database**: `data/results/test_results.db`
- All test results with success/failure
- Attack details, defense names
- Metrics (latency, tokens)

**Exports**: `data/exports/`
- `experiment_results.csv` - All raw data
- `summary_statistics.json` - Stats
- `defense_comparison.md` - Tables
- `visualizations/*.png` - Charts

---

## New Features Summary

### New Attack Categories

**1. Adversarial Techniques** (10 attacks)
- Unicode homoglyphs, leetspeak, zero-width chars
- ASCII art, character substitution, encoding
- File: `data/attacks/adversarial_techniques.json`

**2. Multi-Turn Attacks** (8 attacks)
- Gradual jailbreak, context poisoning
- Role drift, conversation hijacking
- File: `data/attacks/multi_turn.json`

### New Defense Mechanisms

**1. InstructionHierarchy** (No ML required)
- Enforces system instruction priority
- Prompt engineering approach
- Zero latency overhead

**2. PerplexityFilter** (Requires: transformers, torch)
- Detects obfuscated/encoded inputs
- ML-based anomaly detection
- Effective against adversarial techniques

**3. SemanticSimilarity** (Requires: sentence-transformers)
- Detects paraphrased attacks
- Embedding-based matching
- Effective against multi-turn attacks

---

## Documentation

Read these for more details:

- `IMPLEMENTATION_COMPLETE.md` - Full implementation details
- `PROJECT_REVIEW_AND_RECOMMENDATIONS.md` - Original review
- `README.md` - Project overview
- `QUICKSTART.md` - Setup guide

---

## Troubleshooting

**Problem**: Module not found errors
**Solution**: Install dependencies or run without ML

**Problem**: Ollama connection failed
**Solution**: `ollama serve` then `ollama list`

**Problem**: Out of memory
**Solution**: Use GPT-4 API or run in smaller batches

**Problem**: Tests taking too long
**Solution**: Use GPT-4 (much faster) or reduce batch size

---

## Recommended Workflow

**TODAY** (Testing):
1. Test: `python scripts/test_new_features.py`
2. Demo: `python scripts/run_simple_test.py`

**LATER** (Data Collection):
- Choose Option 1, 2, or 3 above

**FINAL** (Thesis):
1. Generate report
2. Use data from `data/exports/`
3. Include visualizations in thesis

---

**🎉 You're ready to collect thesis data!**

**Start with**: `python scripts/test_new_features.py`

**Then choose an option above and run experiments!**