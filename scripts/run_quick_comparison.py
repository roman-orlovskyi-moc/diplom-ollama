#!/usr/bin/env python3
"""
Quick Comparison - Fast and cheap testing with smart sampling

This script uses stratified sampling to test representative attacks while
maintaining statistical validity. Perfect for:
- Quick hypothesis testing
- Preliminary results
- Budget-conscious research
- Iterative development

Strategy:
- 5 attacks per category (stratified by severity)
- 5 most effective defenses
- All available models
- ~75 total tests (vs ~1050 in full)
- ~$2-5 cost (vs ~$15-30)
- ~10 minutes (vs ~45-60)
"""
import sys
import os
from pathlib import Path
from tqdm import tqdm
import json
import random
from datetime import datetime
from collections import defaultdict

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
from config.settings import (
    OPENAI_API_KEY, ANTHROPIC_API_KEY,
    DEFAULT_OLLAMA_MODEL, DEFAULT_OPENAI_MODEL, DEFAULT_ANTHROPIC_MODEL
)


def get_available_models():
    """Check which models are available"""
    models = []

    # Ollama (always available)
    models.append({
        'name': 'Llama3.2',
        'provider': LLMProvider.OLLAMA,
        'config': {
            'base_url': 'http://localhost:11434',
            'model': DEFAULT_OLLAMA_MODEL
        }
    })

    # OpenAI
    if OPENAI_API_KEY:
        models.append({
            'name': 'GPT-4o',
            'provider': LLMProvider.OPENAI,
            'config': {
                'api_key': OPENAI_API_KEY,
                'model': DEFAULT_OPENAI_MODEL
            }
        })

    # Anthropic
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


def get_top_defenses():
    """
    Get the 5 most important defenses to test
    Based on literature and expected effectiveness
    """
    return [
        ('NoDefense', None),
        ('InputSanitizer', InputSanitizer()),
        ('PromptTemplate-XML', PromptTemplate({'template_style': 'xml'})),
        ('ContextIsolation', ContextIsolation()),
        ('InstructionHierarchy', InstructionHierarchy()),
    ]


def stratified_sample_attacks(attack_engine, n_per_category=5):
    """
    Stratified sampling: select N attacks per category,
    ensuring coverage of different severity levels

    This maintains representativeness while reducing sample size
    """
    sampled_attacks = []

    for category in attack_engine.get_categories():
        cat_attacks = attack_engine.get_attacks_by_category(category)

        # Group by severity
        by_severity = defaultdict(list)
        for attack in cat_attacks:
            by_severity[attack.severity].append(attack)

        # Sample from each severity level
        category_sample = []
        severities = ['low', 'medium', 'high', 'critical']

        # Calculate how many from each severity
        n_severities = len([s for s in severities if by_severity[s]])
        per_severity = max(1, n_per_category // n_severities)

        for severity in severities:
            if by_severity[severity]:
                n_sample = min(per_severity, len(by_severity[severity]))
                category_sample.extend(random.sample(by_severity[severity], n_sample))

        # If we need more to reach n_per_category, sample randomly
        while len(category_sample) < n_per_category and len(category_sample) < len(cat_attacks):
            remaining = [a for a in cat_attacks if a not in category_sample]
            if remaining:
                category_sample.append(random.choice(remaining))

        sampled_attacks.extend(category_sample[:n_per_category])

        print(f"   {category}: {len(category_sample)} attacks (from {len(cat_attacks)} total)")

    return sampled_attacks


def calculate_asr_der(results):
    """Calculate Attack Success Rate and Defense Effectiveness Rate"""
    if not results:
        return 0.0, 0.0

    total = len(results)
    successful = sum(1 for r in results if r.attack_successful)

    asr = (successful / total) * 100
    der = 100 - asr

    return asr, der


def calculate_confidence_interval(results, confidence=0.95):
    """
    Calculate confidence interval for ASR

    This shows the statistical validity of our sampling
    """
    import math

    if not results:
        return 0, 0

    n = len(results)
    p = sum(1 for r in results if r.attack_successful) / n

    # Standard error
    se = math.sqrt(p * (1 - p) / n)

    # Z-score for 95% confidence
    z = 1.96

    # Confidence interval
    margin = z * se * 100

    return margin


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"{title.center(80)}")
    print("=" * 80)


def export_results(all_results, output_dir):
    """Export results to CSV and JSON"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # CSV
    csv_path = output_dir / 'quick_comparison_results.csv'
    with open(csv_path, 'w') as f:
        f.write('Model,Defense,Tests,Successful,ASR(%),DER(%),CI(±%),Avg_Latency_ms,Total_Cost\n')

        for model_name, model_results in all_results.items():
            for defense_name, results in model_results.items():
                if results:
                    asr, der = calculate_asr_der(results)
                    ci = calculate_confidence_interval(results)
                    total = len(results)
                    successful = sum(1 for r in results if r.attack_successful)
                    avg_latency = sum(r.latency_ms for r in results) / total
                    total_cost = sum(r.cost for r in results)

                    f.write(f'{model_name},{defense_name},{total},{successful},'
                           f'{asr:.2f},{der:.2f},{ci:.2f},{avg_latency:.1f},{total_cost:.4f}\n')

    print(f"✓ CSV exported to: {csv_path}")

    # JSON with metadata
    json_data = {
        'timestamp': datetime.now().isoformat(),
        'sampling_method': 'stratified',
        'confidence_level': '95%',
        'models_tested': list(all_results.keys()),
        'results': {}
    }

    for model_name, model_results in all_results.items():
        json_data['results'][model_name] = {}
        for defense_name, results in model_results.items():
            if results:
                asr, der = calculate_asr_der(results)
                ci = calculate_confidence_interval(results)

                json_data['results'][model_name][defense_name] = {
                    'total_tests': len(results),
                    'successful_attacks': sum(1 for r in results if r.attack_successful),
                    'asr': asr,
                    'der': der,
                    'confidence_interval': ci,
                    'note': f'Results ±{ci:.1f}% with 95% confidence'
                }

    json_path = output_dir / 'quick_comparison_results.json'
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)

    print(f"✓ JSON exported to: {json_path}")

    return csv_path, json_path


def print_comparison_table(all_results):
    """Print formatted comparison table with confidence intervals"""
    print_section("QUICK COMPARISON RESULTS")

    print(f"\n{'Model':<20} {'Defense':<25} {'Tests':<7} {'ASR (%)':<12} {'DER (%)':<12} {'CI (±%)'}")
    print("-" * 90)

    for model_name, model_results in all_results.items():
        for defense_name, results in model_results.items():
            if results:
                asr, der = calculate_asr_der(results)
                ci = calculate_confidence_interval(results)

                print(
                    f"{model_name:<20} "
                    f"{defense_name:<25} "
                    f"{len(results):<7} "
                    f"{asr:>6.2f}%     "
                    f"{der:>6.2f}%     "
                    f"±{ci:.2f}%"
                )

    print("\n* CI = Confidence Interval (95% confidence level)")
    print("  Smaller CI = More reliable result")
    print("  With 25 tests per config, CI is typically ±10-15%")


def print_conclusions(all_results):
    """Generate conclusions from quick comparison"""
    print_section("CONCLUSIONS (QUICK COMPARISON)")

    print("\n⚠ STATISTICAL NOTE:")
    print("   This is a stratified sample providing preliminary insights.")
    print("   Confidence intervals show statistical reliability.")
    print("   For publication-quality results, run full comparison.")

    # Find best defense per model
    print("\n1. BEST DEFENSE PER MODEL:")
    for model_name, model_results in all_results.items():
        best_defense = None
        best_der = 0.0
        best_ci = 100.0

        for defense_name, results in model_results.items():
            if results and defense_name != 'NoDefense':
                asr, der = calculate_asr_der(results)
                ci = calculate_confidence_interval(results)

                if der > best_der:
                    best_der = der
                    best_defense = defense_name
                    best_ci = ci

        if best_defense:
            print(f"   {model_name}: {best_defense}")
            print(f"      DER: {best_der:.2f}% (±{best_ci:.2f}%)")

    # Model vulnerability
    print("\n2. MODEL VULNERABILITY (NO DEFENSE):")
    vulnerabilities = []
    for model_name, model_results in all_results.items():
        if 'NoDefense' in model_results and model_results['NoDefense']:
            asr, der = calculate_asr_der(model_results['NoDefense'])
            ci = calculate_confidence_interval(model_results['NoDefense'])
            vulnerabilities.append((model_name, asr, ci))

    vulnerabilities.sort(key=lambda x: x[1], reverse=True)
    for model_name, asr, ci in vulnerabilities:
        print(f"   {model_name}: {asr:.2f}% ASR (±{ci:.2f}%)")

    # Overall best defense
    print("\n3. OVERALL BEST DEFENSE:")
    defense_scores = {}
    for model_name, model_results in all_results.items():
        for defense_name, results in model_results.items():
            if results and defense_name != 'NoDefense':
                asr, der = calculate_asr_der(results)
                if defense_name not in defense_scores:
                    defense_scores[defense_name] = []
                defense_scores[defense_name].append(der)

    best_defense = max(defense_scores.items(), key=lambda x: sum(x[1])/len(x[1]))
    avg_der = sum(best_defense[1]) / len(best_defense[1])

    print(f"   {best_defense[0]}")
    print(f"   Average DER: {avg_der:.2f}% across {len(best_defense[1])} models")

    # Recommendations
    print("\n4. RECOMMENDATIONS:")
    print("   ✓ Run full comparison for publication")
    print("   ✓ These results are valid for preliminary analysis")
    print("   ✓ Focus on defenses showing >70% DER")
    print("   ✓ Test additional defenses if needed")


def main():
    """Run quick comparison with smart sampling"""
    print_section("QUICK COMPARISON - SMART SAMPLING")

    print("\n📊 SAMPLING STRATEGY:")
    print("   • 5 attacks per category (stratified by severity)")
    print("   • 5 most effective defenses")
    print("   • All available models")
    print("   • ~75 total tests (vs ~1050 full)")
    print("   • 95% confidence intervals provided")
    print("   • Results valid for preliminary analysis")

    # Check models
    print("\n1. Checking available models...")
    models = get_available_models()
    print(f"   ✓ Found {len(models)} models: {', '.join(m['name'] for m in models)}")

    # Load and sample attacks
    print("\n2. Loading and sampling attacks...")
    attack_engine = AttackEngine()
    attack_engine.load_attacks()

    print("\n   Stratified sampling (5 per category, balanced by severity):")
    attacks = stratified_sample_attacks(attack_engine, n_per_category=5)
    print(f"\n   ✓ Selected {len(attacks)} representative attacks")

    # Get defenses
    print("\n3. Top defenses to test...")
    defenses = get_top_defenses()
    for name, _ in defenses:
        print(f"   • {name}")

    # Calculate experiment size
    total_tests = len(attacks) * len(defenses) * len(models)
    estimated_time_min = (total_tests * 3) / 60

    # Estimate cost
    api_models = [m for m in models if m['provider'] != LLMProvider.OLLAMA]
    est_cost_min = len(api_models) * len(attacks) * len(defenses) * 0.0015
    est_cost_max = len(api_models) * len(attacks) * len(defenses) * 0.003

    print(f"\n4. Experiment Summary:")
    print(f"   Models: {len(models)}")
    print(f"   Defenses: {len(defenses)}")
    print(f"   Attacks: {len(attacks)}")
    print(f"   Total tests: {total_tests}")
    print(f"   Estimated time: ~{estimated_time_min:.1f} minutes")
    if api_models:
        print(f"   Estimated cost: ${est_cost_min:.2f}-${est_cost_max:.2f}")

    proceed = input("\n   Proceed with quick comparison? (y/N): ")
    if proceed.lower() != 'y':
        print("   Cancelled.")
        return 0

    # Setup database
    db = Database()
    db.create_tables()

    # Run experiments
    print_section("RUNNING QUICK COMPARISON")

    all_results = {}

    for model_info in models:
        model_name = model_info['name']
        print(f"\n\n📱 Testing: {model_name}")
        print("-" * 80)

        try:
            client = LLMClientFactory.create(
                model_info['provider'],
                **model_info['config']
            )
            print(f"✓ Connected")
        except Exception as e:
            print(f"✗ Error: {e}")
            continue

        eval_engine = EvaluationEngine(client, db)
        model_results = {}

        for defense_name, defense in defenses:
            results = []

            with tqdm(total=len(attacks), desc=f"  {defense_name:25s}",
                     unit="test") as pbar:
                for attack in attacks:
                    try:
                        result = eval_engine.evaluate_attack(attack, defense)
                        results.append(result)

                        asr, der = calculate_asr_der(results)
                        pbar.set_postfix({'ASR': f"{asr:.1f}%"})
                        pbar.update(1)
                    except Exception as e:
                        pbar.update(1)

            model_results[defense_name] = results

            if results:
                asr, der = calculate_asr_der(results)
                ci = calculate_confidence_interval(results)
                print(f"    ASR: {asr:.2f}% (±{ci:.2f}%) | DER: {der:.2f}%")

        all_results[model_name] = model_results

    # Results
    print_comparison_table(all_results)

    # Export
    print_section("EXPORTING RESULTS")
    export_dir = Path('data/exports')
    csv_path, json_path = export_results(all_results, export_dir)

    # Conclusions
    print_conclusions(all_results)

    # Summary
    print_section("QUICK COMPARISON COMPLETE")

    print("\n✓ Quick comparison finished!")
    print(f"\nGenerated files:")
    print(f"  • {csv_path}")
    print(f"  • {json_path}")

    print("\n📈 STATISTICAL VALIDITY:")
    print(f"  • Sample size: {len(attacks)} attacks (stratified)")
    print(f"  • Confidence level: 95%")
    print(f"  • Typical margin of error: ±10-15%")
    print(f"  • Valid for: Preliminary analysis, hypothesis testing")
    print(f"  • Not recommended for: Final publication without full test")

    print("\n🚀 NEXT STEPS:")
    print("  1. Review quick results for preliminary insights")
    print("  2. If results are promising, run full comparison")
    print("  3. Use: python scripts/run_multi_model_comparison.py")
    print("  4. For thesis, cite both quick and full results")

    db.close()
    return 0


if __name__ == '__main__':
    random.seed(42)  # For reproducibility
    sys.exit(main())