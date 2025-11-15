# Usage Examples

Quick code examples for working with the framework.

## Example 1: Load and Explore Attacks

```python
from src.core.attack_engine import AttackEngine

# Load all attacks
engine = AttackEngine()
count = engine.load_attacks()
print(f"Loaded {count} attacks")

# Get statistics
stats = engine.get_statistics()
print(f"Categories: {stats['categories']}")
print(f"Severity distribution: {stats['severity_distribution']}")

# Get specific attack
attack = engine.get_attack_by_id('di_001')
print(f"Attack: {attack.name}")
print(f"Description: {attack.description}")
print(f"System prompt: {attack.context.system_prompt}")
print(f"User message: {attack.context.user_message}")

# Get all jailbreak attacks
jailbreaks = engine.get_attacks_by_category('jailbreak')
print(f"Found {len(jailbreaks)} jailbreak attacks")

# Get high severity attacks
high_severity = engine.get_attacks_by_severity('high')
print(f"Found {len(high_severity)} high severity attacks")
```

## Example 2: Test Single Attack Without Defense

```python
from src.core.attack_engine import AttackEngine
from src.core.llm_client import LLMClientFactory, LLMProvider
from src.core.evaluation import EvaluationEngine

# Setup
engine = AttackEngine()
engine.load_attacks()

client = LLMClientFactory.create(LLMProvider.OLLAMA)
eval_engine = EvaluationEngine(client)

# Get attack
attack = engine.get_attack_by_id('di_001')

# Test without defense
result = eval_engine.evaluate_attack(attack, defense=None)

print(f"Attack: {attack.name}")
print(f"Successful: {result.attack_successful}")
print(f"Latency: {result.latency_ms}ms")
print(f"Response: {result.response}")
```

## Example 3: Test Attack With Defense

```python
from src.core.attack_engine import AttackEngine
from src.core.llm_client import LLMClientFactory, LLMProvider
from src.core.evaluation import EvaluationEngine
from src.defenses.input_sanitizer import InputSanitizer

# Setup
engine = AttackEngine()
engine.load_attacks()

client = LLMClientFactory.create(LLMProvider.OLLAMA)
eval_engine = EvaluationEngine(client)

# Create defense
defense = InputSanitizer()

# Get attack
attack = engine.get_attack_by_id('di_001')

# Test with defense
result = eval_engine.evaluate_attack(attack, defense=defense)

print(f"Attack: {attack.name}")
print(f"Defense: {defense.name}")
print(f"Successful: {result.attack_successful}")
print(f"Response: {result.response}")
```

## Example 4: Compare Multiple Defenses

```python
from src.core.attack_engine import AttackEngine
from src.core.llm_client import LLMClientFactory, LLMProvider
from src.core.evaluation import EvaluationEngine
from src.defenses.input_sanitizer import InputSanitizer
from src.defenses.prompt_template import PromptTemplate
from src.defenses.output_filter import OutputFilter

# Setup
engine = AttackEngine()
engine.load_attacks()

client = LLMClientFactory.create(LLMProvider.OLLAMA)
eval_engine = EvaluationEngine(client)

# Get attack
attack = engine.get_attack_by_id('jb_001')  # DAN jailbreak

# Test with different defenses
defenses = [
    ('No Defense', None),
    ('Input Sanitizer', InputSanitizer()),
    ('Prompt Template', PromptTemplate()),
    ('Output Filter', OutputFilter())
]

print(f"Testing: {attack.name}\n")

for name, defense in defenses:
    result = eval_engine.evaluate_attack(attack, defense)
    status = "BLOCKED" if not result.attack_successful else "SUCCEEDED"
    print(f"{name:20} -> Attack {status}")
```

## Example 5: Test Category of Attacks

```python
from src.core.attack_engine import AttackEngine
from src.core.llm_client import LLMClientFactory, LLMProvider
from src.core.evaluation import EvaluationEngine
from src.defenses.prompt_template import PromptTemplate

# Setup
engine = AttackEngine()
engine.load_attacks()

client = LLMClientFactory.create(LLMProvider.OLLAMA)
eval_engine = EvaluationEngine(client)

# Get all jailbreak attacks
attacks = engine.get_attacks_by_category('jailbreak')

# Create defense
defense = PromptTemplate()

# Test all attacks
results = []
for attack in attacks:
    result = eval_engine.evaluate_attack(attack, defense)
    results.append(result)
    status = "BLOCKED" if not result.attack_successful else "SUCCEEDED"
    print(f"{attack.name:30} -> {status}")

# Calculate metrics
metrics = eval_engine.calculate_metrics(results)
print(f"\nOverall Results:")
print(f"Attack Success Rate: {metrics['attack_success_rate']*100:.1f}%")
print(f"Defense Effectiveness: {metrics['defense_effectiveness_rate']*100:.1f}%")
```

## Example 6: Use Database

```python
from src.core.attack_engine import AttackEngine
from src.core.llm_client import LLMClientFactory, LLMProvider
from src.core.evaluation import EvaluationEngine
from src.utils.database import Database
from src.defenses.input_sanitizer import InputSanitizer

# Setup with database
engine = AttackEngine()
engine.load_attacks()

client = LLMClientFactory.create(LLMProvider.OLLAMA)
db = Database()
eval_engine = EvaluationEngine(client, db)  # Pass database

# Test attacks (results automatically saved)
defense = InputSanitizer()
attacks = engine.get_attacks_by_severity('high')

for attack in attacks[:5]:  # Test first 5
    result = eval_engine.evaluate_attack(attack, defense)
    print(f"Tested {attack.id}: {'BLOCKED' if not result.attack_successful else 'SUCCEEDED'}")

# Query database
all_results = db.get_all_results()
print(f"\nTotal tests in database: {len(all_results)}")

defense_results = db.get_results_by_defense('InputSanitizer')
print(f"Tests for InputSanitizer: {len(defense_results)}")

# Get statistics
stats = db.get_statistics()
print(f"Overall success rate: {stats['successful_attacks']/stats['total_tests']*100:.1f}%")

# Export to CSV
db.export_to_csv(Path('my_results.csv'))

db.close()
```

## Example 7: Custom Defense Configuration

```python
from src.defenses.input_sanitizer import InputSanitizer
from src.defenses.prompt_template import PromptTemplate
from src.defenses.output_filter import OutputFilter

# Custom Input Sanitizer with custom blocklist
custom_sanitizer = InputSanitizer(config={
    'blocklist_patterns': [
        r'hack',
        r'exploit',
        r'bypass',
        r'override'
    ],
    'max_length': 1000
})

# Custom Prompt Template with XML style
xml_template = PromptTemplate(config={
    'template_style': 'xml'
})

# Custom Output Filter with custom threshold
strict_filter = OutputFilter(config={
    'overlap_threshold': 0.2,  # More strict (default 0.3)
    'block_message': 'Security filter activated.'
})

# Use them
user_input = "Hack into the system"
system_prompt = "You are a helper"

protected = custom_sanitizer.protect_input(user_input, system_prompt)
print(f"Sanitized: {protected['user_input']}")
```

## Example 8: Batch Testing with Progress

```python
from src.core.attack_engine import AttackEngine
from src.core.llm_client import LLMClientFactory, LLMProvider
from src.core.evaluation import EvaluationEngine
from src.defenses.prompt_template import PromptTemplate
from tqdm import tqdm

# Setup
engine = AttackEngine()
engine.load_attacks()

client = LLMClientFactory.create(LLMProvider.OLLAMA)
eval_engine = EvaluationEngine(client)

defense = PromptTemplate()
attacks = engine.get_all_attacks()

# Test with progress bar
results = []
with tqdm(total=len(attacks), desc="Testing attacks") as pbar:
    for attack in attacks:
        result = eval_engine.evaluate_attack(attack, defense)
        results.append(result)

        # Update progress with stats
        successful = sum(1 for r in results if r.attack_successful)
        pbar.set_postfix({
            'successful': f"{successful}/{len(results)}",
            'rate': f"{successful/len(results)*100:.1f}%"
        })
        pbar.update(1)

# Show final metrics
metrics = eval_engine.calculate_metrics(results)
print(f"\nFinal metrics:")
print(f"Total tests: {metrics['total_tests']}")
print(f"Attack success rate: {metrics['attack_success_rate']*100:.1f}%")
print(f"Avg latency: {metrics['avg_latency_ms']:.0f}ms")
```

## Example 9: Using Different LLM Providers

```python
from src.core.llm_client import LLMClientFactory, LLMProvider

# Ollama (local, free)
ollama_client = LLMClientFactory.create(
    LLMProvider.OLLAMA,
    base_url='http://localhost:11434',
    model='llama3.2'
)

# OpenAI (requires API key)
openai_client = LLMClientFactory.create(
    LLMProvider.OPENAI,
    api_key='your-api-key-here',
    model='gpt-4'
)

# Anthropic Claude (requires API key)
anthropic_client = LLMClientFactory.create(
    LLMProvider.ANTHROPIC,
    api_key='your-api-key-here',
    model='claude-3-5-sonnet-20241022'
)

# Test with any client
result = ollama_client.generate(
    prompt="Hello, how are you?",
    system_prompt="You are a friendly assistant.",
    max_tokens=100,
    temperature=0.7
)

print(f"Response: {result['response']}")
print(f"Tokens: {result['tokens_used']}")
print(f"Cost: ${result['cost']}")
```

## Example 10: Full Workflow Example

```python
#!/usr/bin/env python3
"""
Complete example: Load attacks, test with multiple defenses, save results
"""
from pathlib import Path
from src.core.attack_engine import AttackEngine
from src.core.llm_client import LLMClientFactory, LLMProvider
from src.core.evaluation import EvaluationEngine
from src.utils.database import Database
from src.defenses.input_sanitizer import InputSanitizer
from src.defenses.prompt_template import PromptTemplate
from src.defenses.output_filter import OutputFilter

def main():
    print("Setting up...")

    # Initialize components
    engine = AttackEngine()
    engine.load_attacks()

    client = LLMClientFactory.create(LLMProvider.OLLAMA)
    db = Database()
    db.create_tables()

    eval_engine = EvaluationEngine(client, db)

    # Define test configuration
    defenses = [
        ('No Defense', None),
        ('Input Sanitizer', InputSanitizer()),
        ('Prompt Template', PromptTemplate()),
        ('Output Filter', OutputFilter())
    ]

    # Get attacks to test (let's test critical severity)
    attacks = engine.get_attacks_by_severity('critical')
    print(f"Testing {len(attacks)} critical attacks with {len(defenses)} defenses")

    # Run tests
    results_by_defense = {}

    for defense_name, defense in defenses:
        print(f"\nTesting with: {defense_name}")
        results = []

        for attack in attacks:
            result = eval_engine.evaluate_attack(attack, defense)
            results.append(result)
            print(f"  {attack.id}: {'BLOCKED' if not result.attack_successful else 'SUCCEEDED'}")

        results_by_defense[defense_name] = results

    # Calculate and display comparison
    print("\n" + "="*60)
    print("COMPARISON")
    print("="*60)

    comparison = eval_engine.compare_defenses(results_by_defense)

    for defense_name, metrics in comparison.items():
        print(f"\n{defense_name}:")
        print(f"  Attack Success Rate: {metrics['attack_success_rate']*100:.1f}%")
        print(f"  Defense Effectiveness: {metrics['defense_effectiveness_rate']*100:.1f}%")
        print(f"  Avg Latency: {metrics['avg_latency_ms']:.0f}ms")

    # Export results
    export_path = Path('data/exports/my_test_results.csv')
    db.export_to_csv(export_path)
    print(f"\n✓ Results exported to: {export_path}")

    db.close()

if __name__ == '__main__':
    main()
```

## Tips

- Always activate virtual environment first: `source venv/bin/activate`
- Import from `src.` package (e.g., `from src.core.attack_engine import AttackEngine`)
- Results are automatically saved if you pass `database` to `EvaluationEngine`
- Use `tqdm` for progress bars in long-running tests
- Check `scripts/` directory for more complete examples