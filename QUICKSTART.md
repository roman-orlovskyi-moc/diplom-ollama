# Quick Start Guide

## Prerequisites

1. **Python 3.10+** with venv installed
2. **Ollama** installed and running

## Setup (One-time)

### 1. Install Virtual Environment Support

```bash
sudo apt install python3.12-venv -y
```

### 2. Create and Activate Virtual Environment

```bash
cd /home/master/www/diplom
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and Configure Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull llama3.2

# Verify installation
ollama list

# Start Ollama server (if not already running)
ollama serve &
```

### 5. Initialize Database

```bash
python scripts/setup_db.py
```

## Verify Setup

Run the test suite to verify everything is working:

```bash
python scripts/test_setup.py
```

This will check:
- All Python modules can be imported
- Attack patterns are loaded correctly
- LLM client can connect to Ollama
- Database operations work

## Running Tests

### Quick Test (Single Attack)

Test one attack with multiple defenses:

```bash
python scripts/run_simple_test.py
```

This will:
- Load attack pattern 'di_001'
- Test it without defense
- Test it with InputSanitizer
- Test it with PromptTemplate
- Show comparison results

### Full Experiment Suite

Run comprehensive testing of all attacks against all defenses:

```bash
python scripts/run_experiments.py
```

This will:
- Load all 56 attack patterns
- Test each attack against 5-6 defense mechanisms
- Save results to database
- Export CSV for analysis
- Show detailed comparison

**Note**: Full experiments take ~15-30 minutes depending on your system.

### Generate Thesis Report

After running experiments, generate visualizations and analysis:

```bash
python scripts/generate_report.py
```

This will create:
- Summary statistics (JSON)
- Defense comparison table (Markdown)
- Category analysis (Markdown)
- Visualizations (PNG charts)

## Project Structure

```
diplom/
├── data/
│   ├── attacks/           # 56 attack patterns in JSON
│   ├── results/           # SQLite database with test results
│   └── exports/           # Generated reports and visualizations
├── src/
│   ├── models/            # Data models (Attack, TestResult)
│   ├── core/              # Core logic (AttackEngine, Evaluation, LLM)
│   ├── defenses/          # Defense mechanisms (5 implementations)
│   └── utils/             # Database and utilities
├── scripts/               # Executable scripts
└── tests/                 # Unit tests
```

## Defense Mechanisms Implemented

1. **NoDefense** - Baseline (no protection)
2. **InputSanitizer** - Blocklist-based input filtering
3. **PromptTemplate** - Delimited prompt structure
4. **PromptTemplateXML** - XML-style prompt structure
5. **OutputFilter** - Response content filtering
6. **ContextIsolation** - XML-based context separation
7. **DualLLM** (optional) - Guardian model verification

## Attack Categories

1. **direct_injection** (12 attacks) - Direct instruction override
2. **jailbreak** (12 attacks) - Safety guideline bypass
3. **role_confusion** (12 attacks) - Identity/role manipulation
4. **context_switching** (12 attacks) - Format/language switching
5. **indirect_injection** (8 attacks) - Injection via external data
6. **data_extraction** (10 attacks) - System prompt/data leakage

## Common Workflows

### Workflow 1: Quick Demo

```bash
# Activate environment
source venv/bin/activate

# Run simple test
python scripts/run_simple_test.py
```

### Workflow 2: Full Research Data Collection

```bash
# Activate environment
source venv/bin/activate

# Run comprehensive experiments
python scripts/run_experiments.py

# Generate thesis report
python scripts/generate_report.py

# Check results
ls data/exports/
cat data/exports/defense_comparison.md
```

### Workflow 3: Custom Testing

```python
# Create custom test script
from src.core.attack_engine import AttackEngine
from src.core.llm_client import LLMClientFactory, LLMProvider
from src.core.evaluation import EvaluationEngine
from src.defenses.input_sanitizer import InputSanitizer

# Load attacks
engine = AttackEngine()
engine.load_attacks()

# Get specific attacks
jailbreak_attacks = engine.get_attacks_by_category('jailbreak')
high_severity = engine.get_attacks_by_severity('high')

# Create LLM client
client = LLMClientFactory.create(LLMProvider.OLLAMA)

# Test with defense
eval_engine = EvaluationEngine(client)
defense = InputSanitizer()

for attack in jailbreak_attacks[:5]:  # Test first 5
    result = eval_engine.evaluate_attack(attack, defense)
    print(f"{attack.name}: {'BLOCKED' if not result.attack_successful else 'FAILED'}")
```

## Troubleshooting

### Ollama Not Connecting

```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve &

# Test connection
ollama list
```

### Import Errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Errors

```bash
# Recreate database
rm data/results/test_results.db
python scripts/setup_db.py
```

### Out of Memory

If testing all attacks causes memory issues:

1. Edit `scripts/run_experiments.py`
2. Choose option 4 (Quick test) or option 2 (Test by category)
3. Test categories one at a time

## Next Steps for Thesis

1. **Run full experiments** to collect comprehensive data
2. **Generate report** with visualizations
3. **Analyze results**:
   - Which defenses are most effective?
   - Which attack categories are hardest to defend?
   - What's the trade-off between security and performance?
4. **Include in thesis**:
   - Methodology from `PROJECT_IMPLEMENTATION_GUIDE.md`
   - Results from `data/exports/`
   - Visualizations from `data/exports/visualizations/`
   - Analysis from comparison tables

## Getting Help

- **Implementation details**: See `PROJECT_IMPLEMENTATION_GUIDE.md`
- **Progress tracking**: See `PROGRESS.md`
- **Project overview**: See `README.md`

## Tips

- Always activate virtual environment: `source venv/bin/activate`
- Start with simple test before running full experiments
- Full experiments can be interrupted (Ctrl+C) - results are saved incrementally
- Export CSV can be opened in Excel/LibreOffice for additional analysis
- Visualizations are publication-ready (300 DPI PNG)