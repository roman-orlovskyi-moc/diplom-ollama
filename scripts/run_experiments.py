#!/usr/bin/env python3
"""
Run Experiments - Comprehensive testing of all attacks against all defenses
"""
import sys
from pathlib import Path
from tqdm import tqdm

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
from src.defenses.dual_llm import DualLLM


def main():
    """Run comprehensive experiments"""
    print("=" * 80)
    print("COMPREHENSIVE PROMPT INJECTION DEFENSE EVALUATION")
    print("=" * 80)

    # Setup
    print("\n1. Initializing components...")

    # Load attacks
    attack_engine = AttackEngine()
    attack_count = attack_engine.load_attacks()
    print(f"   ✓ Loaded {attack_count} attack patterns")

    stats = attack_engine.get_statistics()
    print(f"   ✓ Categories: {len(stats['categories'])}")
    for cat, count in stats['categories'].items():
        print(f"      - {cat}: {count}")

    # Initialize LLM client
    print("\n2. Connecting to LLM...")
    try:
        client = LLMClientFactory.create(
            LLMProvider.OLLAMA,
            base_url='http://localhost:11434',
            model='llama3.2'
        )
        print("   ✓ Ollama client ready")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        print("\n   Please make sure Ollama is running:")
        print("   - Install: curl -fsSL https://ollama.com/install.sh | sh")
        print("   - Pull model: ollama pull llama3.2")
        print("   - Start: ollama serve")
        return 1

    # Initialize database
    print("\n3. Setting up database...")
    db = Database()
    db.create_tables()
    print("   ✓ Database ready")

    # Ask about clearing previous results
    print("\n   Current database statistics:")
    db_stats = db.get_statistics()
    if db_stats['total_tests'] > 0:
        print(f"   - Total previous tests: {db_stats['total_tests']}")
        response = input("\n   Clear previous results? (y/N): ")
        if response.lower() == 'y':
            db.clear_all()
            print("   ✓ Database cleared")

    # Initialize evaluation engine
    eval_engine = EvaluationEngine(client, db)

    # Define defenses to test
    print("\n4. Preparing defense mechanisms...")
    defenses = [
        ('NoDefense', None),
        ('InputSanitizer', InputSanitizer()),
        ('PromptTemplate', PromptTemplate({'template_style': 'delimited'})),
        ('PromptTemplateXML', PromptTemplate({'template_style': 'xml'})),
        ('OutputFilter', OutputFilter()),
        ('ContextIsolation', ContextIsolation()),
    ]

    # Add DualLLM if user wants (expensive)
    use_dual = input("\n   Include DualLLM defense? (doubles LLM calls, slower) (y/N): ")
    if use_dual.lower() == 'y':
        guardian_client = LLMClientFactory.create(
            LLMProvider.OLLAMA,
            base_url='http://localhost:11434',
            model='llama3.2'
        )
        defenses.append(('DualLLM', DualLLM({'guardian_client': guardian_client})))

    print(f"   ✓ Testing {len(defenses)} defense configurations")

    # Get attacks to test
    attacks = attack_engine.get_all_attacks()

    # Option to filter attacks
    print(f"\n5. Attack selection ({len(attacks)} total attacks available)")
    print("   Options:")
    print("   1. Test all attacks (recommended for thesis)")
    print("   2. Test by category")
    print("   3. Test by severity")
    print("   4. Quick test (10 random attacks)")

    choice = input("\n   Choice (1-4): ").strip()

    if choice == '2':
        print(f"\n   Categories: {', '.join(attack_engine.get_categories())}")
        cat = input("   Enter category: ").strip()
        attacks = attack_engine.get_attacks_by_category(cat)
        print(f"   ✓ Selected {len(attacks)} attacks from category '{cat}'")
    elif choice == '3':
        sev = input("   Enter severity (low/medium/high/critical): ").strip()
        attacks = attack_engine.get_attacks_by_severity(sev)
        print(f"   ✓ Selected {len(attacks)} attacks with severity '{sev}'")
    elif choice == '4':
        import random
        attacks = random.sample(attacks, min(10, len(attacks)))
        print(f"   ✓ Selected {len(attacks)} random attacks")
    else:
        print(f"   ✓ Testing all {len(attacks)} attacks")

    # Confirm before starting
    total_tests = len(attacks) * len(defenses)
    estimated_time_min = (total_tests * 3) / 60  # ~3 seconds per test

    print(f"\n6. Experiment summary:")
    print(f"   - Attacks to test: {len(attacks)}")
    print(f"   - Defense configurations: {len(defenses)}")
    print(f"   - Total tests: {total_tests}")
    print(f"   - Estimated time: ~{estimated_time_min:.1f} minutes")

    proceed = input("\n   Proceed with experiments? (y/N): ")
    if proceed.lower() != 'y':
        print("   Cancelled.")
        return 0

    # Run experiments
    print("\n7. Running experiments...")
    print("=" * 80)

    results_by_defense = {}

    for defense_name, defense in defenses:
        print(f"\n Testing: {defense_name}")
        print("-" * 80)

        results = []
        with tqdm(total=len(attacks), desc=f"  {defense_name:20s}", unit="attack") as pbar:
            for attack in attacks:
                try:
                    result = eval_engine.evaluate_attack(attack, defense)
                    results.append(result)

                    # Update progress bar with current stats
                    successful = sum(1 for r in results if r.attack_successful)
                    pbar.set_postfix({
                        'successful': f"{successful}/{len(results)}",
                        'rate': f"{successful/len(results)*100:.1f}%"
                    })
                    pbar.update(1)

                except Exception as e:
                    print(f"\n  Error testing {attack.id}: {e}")
                    pbar.update(1)
                    continue

        results_by_defense[defense_name] = results

        # Show immediate results for this defense
        if results:
            metrics = eval_engine.calculate_metrics(results)
            print(f"\n  Results for {defense_name}:")
            print(f"    Attack Success Rate: {metrics['attack_success_rate']*100:.1f}%")
            print(f"    Defense Effectiveness: {metrics['defense_effectiveness_rate']*100:.1f}%")
            print(f"    Avg Latency: {metrics['avg_latency_ms']:.0f}ms")
            print(f"    Total Cost: ${metrics['total_cost']:.4f}")

    # Final comparison
    print("\n\n" + "=" * 80)
    print("FINAL RESULTS - DEFENSE COMPARISON")
    print("=" * 80)

    comparison = eval_engine.compare_defenses(results_by_defense)

    print(f"\n{'Defense':<25} {'Tests':<8} {'ASR':<10} {'DER':<10} {'Latency':<12} {'Cost'}")
    print("-" * 80)

    for defense_name in defenses:
        name = defense_name[0]
        if name in comparison:
            c = comparison[name]
            print(
                f"{name:<25} "
                f"{c['total_tests']:<8} "
                f"{c['attack_success_rate']*100:>6.1f}%   "
                f"{c['defense_effectiveness_rate']*100:>6.1f}%   "
                f"{c['avg_latency_ms']:>8.0f}ms   "
                f"${c['total_cost']:>6.4f}"
            )

    # Category breakdown for best defense
    print("\n\nCategory Breakdown (Best Defense):")
    print("-" * 80)

    # Find best defense (lowest ASR)
    best_defense = min(comparison.items(), key=lambda x: x[1]['attack_success_rate'])
    best_name = best_defense[0]
    best_results = results_by_defense[best_name]

    if best_results:
        metrics = eval_engine.calculate_metrics(best_results)
        print(f"\nBest Defense: {best_name}")
        print(f"\nBy Category:")
        for cat, cat_metrics in metrics['by_category'].items():
            print(
                f"  {cat:<20} "
                f"{cat_metrics['successful']}/{cat_metrics['total']:>2} "
                f"({cat_metrics['success_rate']*100:>5.1f}%)"
            )

        print(f"\nBy Severity:")
        for sev in ['low', 'medium', 'high', 'critical']:
            if sev in metrics['by_severity']:
                sev_metrics = metrics['by_severity'][sev]
                print(
                    f"  {sev.capitalize():<20} "
                    f"{sev_metrics['successful']}/{sev_metrics['total']:>2} "
                    f"({sev_metrics['success_rate']*100:>5.1f}%)"
                )

    # Export data
    print("\n\n" + "=" * 80)
    print("EXPORTING DATA")
    print("=" * 80)

    export_path = Path('data/exports/experiment_results.csv')
    db.export_to_csv(export_path)
    print(f"✓ Results exported to: {export_path}")

    print("\nDatabase statistics:")
    final_stats = db.get_statistics()
    print(f"  Total tests in database: {final_stats['total_tests']}")
    print(f"  Successful attacks: {final_stats['successful_attacks']}")

    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review results in data/exports/experiment_results.csv")
    print("2. Generate visualizations for thesis")
    print("3. Analyze defense effectiveness by category and severity")
    print("\nTo generate thesis report, run:")
    print("  python scripts/generate_report.py")

    db.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())