#!/usr/bin/env python3
"""
Multi-Model Comparison - Comprehensive testing across Llama, GPT, and Claude

This script tests all combinations of:
- Attack methods (direct injection, jailbreak, etc.)
- Defense mechanisms (sanitizer, templates, filters, etc.)
- LLM models (Llama 3.2, GPT-4o, Claude Sonnet 4.5)

Generates comprehensive comparison tables with:
- Attack Success Rate (ASR)
- Defense Effectiveness Rate (DER)
- Model-specific analysis
- Best defense recommendations
"""
import sys
import os
from pathlib import Path
from tqdm import tqdm
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.attack_engine import AttackEngine
from src.core.llm_client import LLMClientFactory, LLMProvider
from src.core.evaluation import EvaluationEngine
from src.utils.database import Database
from src.defenses.input_sanitizer import InputSanitizer
from src.defenses.prompt_template import PromptTemplate
from src.defenses.output_filter import OutputFilter
from src.defenses.context_isolation import ContextIsolation
from src.defenses.instruction_hierarchy import InstructionHierarchy
from src.defenses.dual_llm import DualLLM
from src.defenses.perplexity_filter import PerplexityFilter
from src.defenses.semantic_similarity import SemanticSimilarity
from config.settings import (
    OPENAI_API_KEY, ANTHROPIC_API_KEY, OLLAMA_BASE_URL,
    DEFAULT_OLLAMA_MODEL, DEFAULT_OPENAI_MODEL, DEFAULT_ANTHROPIC_MODEL
)


def get_available_models():
    """Check which models are available based on API keys"""
    models = []

    # Ollama is always available (local)
    models.append({
        'name': 'Llama3.2',
        'provider': LLMProvider.OLLAMA,
        'config': {
            'base_url': OLLAMA_BASE_URL,
            'model': DEFAULT_OLLAMA_MODEL
        }
    })

    # Check OpenAI
    if OPENAI_API_KEY:
        models.append({
            'name': 'GPT-4o',
            'provider': LLMProvider.OPENAI,
            'config': {
                'api_key': OPENAI_API_KEY,
                'model': DEFAULT_OPENAI_MODEL
            }
        })

    # Check Anthropic
    if ANTHROPIC_API_KEY:
        models.append({
            'name': 'Claude-Sonnet-4.5',
            'provider': LLMProvider.ANTHROPIC,
            'config': {
                'api_key': ANTHROPIC_API_KEY,
                'model': DEFAULT_ANTHROPIC_MODEL
            }
        })

    return models


def get_defense_configurations():
    """Get all defense mechanisms to test"""

    guardian_client = LLMClientFactory.create(
        LLMProvider.OLLAMA,
        base_url=OLLAMA_BASE_URL,
        model=DEFAULT_OLLAMA_MODEL
    )

    return [
        ('NoDefense', None),
        ('InputSanitizer', InputSanitizer()),
        ('PromptTemplate-Delimited', PromptTemplate({'template_style': 'delimited'})),
        ('PromptTemplate-XML', PromptTemplate({'template_style': 'xml'})),
        ('OutputFilter', OutputFilter()),
        ('ContextIsolation', ContextIsolation()),
        ('InstructionHierarchy', InstructionHierarchy()),
        ('PerplexityFilter', PerplexityFilter()),
        ('SemanticSimilarity', SemanticSimilarity()),
        ('DualLLM', DualLLM({'guardian_client': guardian_client}))
    ]


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"{title.center(80)}")
    print("=" * 80)


def print_subsection(title):
    """Print formatted subsection header"""
    print(f"\n{title}")
    print("-" * 80)


def calculate_asr_der(results):
    """
    Calculate Attack Success Rate and Defense Effectiveness Rate

    ASR = (Successful Attacks / Total Attacks) * 100
    DER = (Blocked Attacks / Total Attacks) * 100 = 100 - ASR
    """
    if not results:
        return 0.0, 0.0

    total = len(results)
    successful = sum(1 for r in results if r.attack_successful)

    asr = (successful / total) * 100
    der = 100 - asr

    return asr, der


def export_comparison_table(all_results, output_dir):
    """Export comprehensive comparison table to CSV and JSON"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create CSV
    csv_path = output_dir / 'model_defense_comparison.csv'
    with open(csv_path, 'w') as f:
        f.write('Model,Defense,Total_Tests,Successful_Attacks,ASR(%),DER(%),Avg_Latency_ms,Total_Cost\n')

        for model_name, model_results in all_results.items():
            for defense_name, results in model_results.items():
                if results:
                    asr, der = calculate_asr_der(results)
                    total = len(results)
                    successful = sum(1 for r in results if r.attack_successful)
                    avg_latency = sum(r.latency_ms for r in results) / total
                    total_cost = sum(r.cost for r in results)

                    f.write(f'{model_name},{defense_name},{total},{successful},'
                           f'{asr:.2f},{der:.2f},{avg_latency:.1f},{total_cost:.4f}\n')

    print(f"✓ CSV exported to: {csv_path}")

    # Create JSON with detailed breakdown
    json_data = {
        'timestamp': datetime.now().isoformat(),
        'models_tested': list(all_results.keys()),
        'results': {}
    }

    for model_name, model_results in all_results.items():
        json_data['results'][model_name] = {}
        for defense_name, results in model_results.items():
            if results:
                asr, der = calculate_asr_der(results)

                # Category breakdown
                by_category = {}
                for result in results:
                    cat = result.attack_category
                    if cat not in by_category:
                        by_category[cat] = {'total': 0, 'successful': 0}
                    by_category[cat]['total'] += 1
                    if result.attack_successful:
                        by_category[cat]['successful'] += 1

                for cat in by_category:
                    by_category[cat]['asr'] = (by_category[cat]['successful'] /
                                              by_category[cat]['total'] * 100)

                json_data['results'][model_name][defense_name] = {
                    'total_tests': len(results),
                    'successful_attacks': sum(1 for r in results if r.attack_successful),
                    'asr': asr,
                    'der': der,
                    'by_category': by_category
                }

    json_path = output_dir / 'model_defense_comparison.json'
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)

    print(f"✓ JSON exported to: {json_path}")

    return csv_path, json_path


def print_comparison_tables(all_results):
    """Print formatted comparison tables"""

    print_section("COMPREHENSIVE COMPARISON TABLES")

    # Table 1: Overall ASR/DER by Model and Defense
    print_subsection("Table 1: Attack Success Rate (ASR) and Defense Effectiveness Rate (DER)")
    print(f"\n{'Model':<20} {'Defense':<25} {'Tests':<8} {'ASR':<10} {'DER':<10} {'Latency':<12}")
    print("-" * 95)

    for model_name, model_results in all_results.items():
        for defense_name, results in model_results.items():
            if results:
                asr, der = calculate_asr_der(results)
                avg_latency = sum(r.latency_ms for r in results) / len(results)
                print(
                    f"{model_name:<20} "
                    f"{defense_name:<25} "
                    f"{len(results):<8} "
                    f"{asr:>6.2f}%   "
                    f"{der:>6.2f}%   "
                    f"{avg_latency:>8.0f}ms"
                )

    # Table 2: Best Defense per Model
    print_subsection("Table 2: Best Defense for Each Model (Lowest ASR)")
    print(f"\n{'Model':<20} {'Best Defense':<25} {'ASR':<10} {'DER':<10}")
    print("-" * 65)

    for model_name, model_results in all_results.items():
        best_defense = None
        best_asr = 100.0

        for defense_name, results in model_results.items():
            if results and defense_name != 'NoDefense':
                asr, der = calculate_asr_der(results)
                if asr < best_asr:
                    best_asr = asr
                    best_defense = defense_name

        if best_defense:
            best_der = 100 - best_asr
            print(
                f"{model_name:<20} "
                f"{best_defense:<25} "
                f"{best_asr:>6.2f}%   "
                f"{best_der:>6.2f}%"
            )

    # Table 3: Model Comparison (NoDefense baseline)
    print_subsection("Table 3: Model Vulnerability (No Defense Baseline)")
    print(f"\n{'Model':<20} {'ASR':<10} {'Most Vulnerable To'}")
    print("-" * 60)

    for model_name, model_results in all_results.items():
        if 'NoDefense' in model_results and model_results['NoDefense']:
            results = model_results['NoDefense']
            asr, _ = calculate_asr_der(results)

            # Find most vulnerable category
            by_category = {}
            for r in results:
                cat = r.attack_category
                if cat not in by_category:
                    by_category[cat] = {'total': 0, 'successful': 0}
                by_category[cat]['total'] += 1
                if r.attack_successful:
                    by_category[cat]['successful'] += 1

            most_vulnerable = max(by_category.items(),
                                 key=lambda x: x[1]['successful']/x[1]['total']
                                 if x[1]['total'] > 0 else 0)

            print(
                f"{model_name:<20} "
                f"{asr:>6.2f}%   "
                f"{most_vulnerable[0]}"
            )

    # Table 4: Defense Performance Across All Models
    print_subsection("Table 4: Defense Performance Across All Models (Average)")

    # Calculate average ASR/DER for each defense across all models
    defense_averages = {}
    for model_name, model_results in all_results.items():
        for defense_name, results in model_results.items():
            if results:
                asr, der = calculate_asr_der(results)
                if defense_name not in defense_averages:
                    defense_averages[defense_name] = {'asr': [], 'der': []}
                defense_averages[defense_name]['asr'].append(asr)
                defense_averages[defense_name]['der'].append(der)

    print(f"\n{'Defense':<30} {'Avg ASR':<12} {'Avg DER':<12} {'Models Tested'}")
    print("-" * 70)

    # Sort by average ASR (best first)
    sorted_defenses = sorted(defense_averages.items(),
                            key=lambda x: sum(x[1]['asr'])/len(x[1]['asr']))

    for defense_name, metrics in sorted_defenses:
        avg_asr = sum(metrics['asr']) / len(metrics['asr'])
        avg_der = sum(metrics['der']) / len(metrics['der'])
        models_count = len(metrics['asr'])

        print(
            f"{defense_name:<30} "
            f"{avg_asr:>8.2f}%   "
            f"{avg_der:>8.2f}%   "
            f"{models_count}"
        )


def print_conclusions(all_results):
    """Generate and print conclusions from the data"""
    print_section("CONCLUSIONS AND RECOMMENDATIONS")

    # Find overall best defense
    defense_scores = {}
    for model_name, model_results in all_results.items():
        for defense_name, results in model_results.items():
            if results and defense_name != 'NoDefense':
                asr, der = calculate_asr_der(results)
                if defense_name not in defense_scores:
                    defense_scores[defense_name] = []
                defense_scores[defense_name].append(der)

    best_overall = max(defense_scores.items(),
                      key=lambda x: sum(x[1])/len(x[1]))

    print(f"\n1. BEST OVERALL DEFENSE: {best_overall[0]}")
    print(f"   Average DER: {sum(best_overall[1])/len(best_overall[1]):.2f}%")
    print(f"   Tested on {len(best_overall[1])} models")

    # Model-specific recommendations
    print(f"\n2. MODEL-SPECIFIC RECOMMENDATIONS:")
    for model_name, model_results in all_results.items():
        best_defense = None
        best_der = 0.0

        for defense_name, results in model_results.items():
            if results and defense_name != 'NoDefense':
                asr, der = calculate_asr_der(results)
                if der > best_der:
                    best_der = der
                    best_defense = defense_name

        if best_defense:
            print(f"   {model_name}: {best_defense} (DER: {best_der:.2f}%)")

    # Weakest defenses
    print(f"\n3. LEAST EFFECTIVE DEFENSES:")
    worst_defenses = sorted(defense_scores.items(),
                           key=lambda x: sum(x[1])/len(x[1]))[:3]

    for defense_name, ders in worst_defenses:
        avg_der = sum(ders) / len(ders)
        print(f"   {defense_name}: Average DER {avg_der:.2f}%")

    # Cost-effectiveness
    print(f"\n4. COST-EFFECTIVENESS ANALYSIS:")
    for model_name, model_results in all_results.items():
        if model_results:
            print(f"   {model_name}:")
            # Find defense with best DER per dollar
            for defense_name, results in model_results.items():
                if results and defense_name != 'NoDefense':
                    asr, der = calculate_asr_der(results)
                    total_cost = sum(r.cost for r in results)
                    if total_cost > 0:
                        efficiency = der / total_cost
                        print(f"      {defense_name}: {der:.1f}% DER at ${total_cost:.4f} (Efficiency: {efficiency:.1f})")
                    else:
                        print(f"      {defense_name}: {der:.1f}% DER (Free/Local)")


def main():
    """Run multi-model comparison"""
    print_section("MULTI-MODEL DEFENSE COMPARISON FOR THESIS")

    # Check available models
    print("\n1. Checking available models...")
    available_models = get_available_models()

    print(f"   ✓ Found {len(available_models)} available models:")
    for model in available_models:
        print(f"      - {model['name']}")

    if len(available_models) < 2:
        print("\n   ⚠ Warning: Only 1 model available.")
        print("   For comprehensive comparison, add API keys to .env:")
        print("      OPENAI_API_KEY=sk-...")
        print("      ANTHROPIC_API_KEY=sk-ant-...")

    # Load attacks
    print("\n2. Loading attack patterns...")
    attack_engine = AttackEngine()
    attack_count = attack_engine.load_attacks()
    print(f"   ✓ Loaded {attack_count} attack patterns")

    stats = attack_engine.get_statistics()
    print(f"   ✓ Categories: {', '.join(stats['categories'].keys())}")

    # Get defenses
    print("\n3. Preparing defense mechanisms...")
    defenses = get_defense_configurations()
    print(f"   ✓ Testing {len(defenses)} defense configurations")

    # Setup database
    print("\n4. Setting up database...")
    db = Database()
    db.create_tables()

    db_stats = db.get_statistics()
    if db_stats['total_tests'] > 0:
        print(f"   ⚠ Found {db_stats['total_tests']} existing tests")
        response = input("   Clear previous results? (y/N): ")
        if response.lower() == 'y':
            db.clear_all()
            print("   ✓ Database cleared")

    # Attack selection
    attacks = attack_engine.get_all_attacks()
    print(f"\n5. Attack selection ({len(attacks)} total)")
    print("   Options:")
    print("   1. All attacks")
    print("   2. Quick test (10 random attacks per category)")

    choice = input("   Choice (1-2): ").strip()

    if choice == '2':
        import random
        # Get representative sample from each category
        sample_attacks = []
        for category in attack_engine.get_categories():
            cat_attacks = attack_engine.get_attacks_by_category(category)
            sample_size = min(10, len(cat_attacks))
            sample_attacks.extend(random.sample(cat_attacks, sample_size))
        attacks = sample_attacks
        print(f"   ✓ Selected {len(attacks)} sample attacks")

    # Calculate experiment size
    total_tests = len(attacks) * len(defenses) * len(available_models)
    estimated_time_min = (total_tests * 3) / 60

    print(f"\n6. Experiment Summary:")
    print(f"   Models: {len(available_models)}")
    print(f"   Defenses: {len(defenses)}")
    print(f"   Attacks: {len(attacks)}")
    print(f"   Total tests: {total_tests}")
    print(f"   Estimated time: ~{estimated_time_min:.1f} minutes")

    # Estimate costs for API models
    api_models = [m for m in available_models if m['provider'] != LLMProvider.OLLAMA]
    if api_models:
        print(f"\n   ⚠ Cost Estimate (API models):")
        for model in api_models:
            tests_per_model = len(attacks) * len(defenses)
            est_tokens = tests_per_model * 500  # ~500 tokens per test
            if 'gpt' in model['name'].lower():
                est_cost = (est_tokens / 1000) * 0.005  # GPT-4o avg cost
            else:
                est_cost = (est_tokens / 1000) * 0.009  # Claude avg cost
            print(f"      {model['name']}: ~${est_cost:.2f}")

    proceed = input("\n   Proceed? (y/N): ")
    if proceed.lower() != 'y':
        print("   Cancelled.")
        return 0

    # Run experiments
    print_section("RUNNING EXPERIMENTS")

    all_results = {}

    for model_info in available_models:
        model_name = model_info['name']
        print(f"\n\nTesting Model: {model_name}")
        print("=" * 80)

        # Create LLM client
        try:
            client = LLMClientFactory.create(
                model_info['provider'],
                **model_info['config']
            )
            print(f"✓ Connected to {model_name}")
        except Exception as e:
            print(f"✗ Error connecting to {model_name}: {e}")
            continue

        # Initialize evaluation engine
        eval_engine = EvaluationEngine(client, db)

        # Test each defense
        model_results = {}

        for defense_name, defense in defenses:
            print(f"\n  Defense: {defense_name}")

            results = []
            with tqdm(total=len(attacks), desc=f"    {defense_name:25s}",
                     unit="attack") as pbar:
                for attack in attacks:
                    try:
                        result = eval_engine.evaluate_attack(attack, defense)
                        results.append(result)

                        successful = sum(1 for r in results if r.attack_successful)
                        asr = (successful / len(results)) * 100
                        pbar.set_postfix({'ASR': f"{asr:.1f}%"})
                        pbar.update(1)
                    except Exception as e:
                        print(f"\n    ✗ Error: {e}")
                        pbar.update(1)

            model_results[defense_name] = results

            # Show immediate results
            if results:
                asr, der = calculate_asr_der(results)
                print(f"    ASR: {asr:.2f}% | DER: {der:.2f}%")

        all_results[model_name] = model_results

    # Generate comparison tables
    print_comparison_tables(all_results)

    # Export data
    print_section("EXPORTING RESULTS")

    export_dir = Path('data/exports')
    csv_path, json_path = export_comparison_table(all_results, export_dir)

    # Export to database CSV
    db_csv = export_dir / 'experiment_results.csv'
    db.export_to_csv(db_csv)
    print(f"✓ Database exported to: {db_csv}")

    # Generate conclusions
    print_conclusions(all_results)

    # Final summary
    print_section("EXPERIMENT COMPLETE")

    print("\n✓ All experiments completed successfully!")
    print("\nGenerated files:")
    print(f"  1. {csv_path}")
    print(f"  2. {json_path}")
    print(f"  3. {db_csv}")
    print("\nNext steps for thesis:")
    print("  1. Use CSV files to create tables in your thesis")
    print("  2. Generate visualizations: python scripts/generate_report.py")
    print("  3. Analyze category-specific performance")
    print("  4. Document cost-effectiveness trade-offs")

    db.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())