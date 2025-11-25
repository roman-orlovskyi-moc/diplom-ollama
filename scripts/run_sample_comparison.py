#!/usr/bin/env python3
"""
Sample Comparison Script - Test defenses with optimized attack sample
Faster alternative to full comparison for slow PCs
"""
import sys
import os
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
from src.defenses.instruction_hierarchy import InstructionHierarchy
from src.defenses.dual_llm import DualLLM
from src.defenses.perplexity_filter import PerplexityFilter
from src.defenses.semantic_similarity import SemanticSimilarity
from config.settings import OLLAMA_BASE_URL, DEFAULT_OLLAMA_MODEL, GUARDIAN_MODEL


def get_sample_attacks(attack_engine, sample_size='balanced'):
    """Get strategic sample of attacks"""
    all_attacks = attack_engine.get_all_attacks()

    if sample_size == 'balanced':  # 40 attacks
        # 5 attacks per category, prioritizing high severity
        categories = attack_engine.get_categories()
        sample = []
        for cat in categories:
            cat_attacks = attack_engine.get_attacks_by_category(cat)
            # Sort by severity
            sorted_attacks = sorted(cat_attacks,
                                   key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.severity, 4))
            sample.extend(sorted_attacks[:5])
        return sample

    elif sample_size == 'strategic':  # 30 attacks
        # Focus on severity
        by_severity = {'critical': [], 'high': [], 'medium': [], 'low': []}
        for attack in all_attacks:
            by_severity[attack.severity].append(attack)

        sample = []
        sample.extend(by_severity['critical'][:5])
        sample.extend(by_severity['high'][:10])
        sample.extend(by_severity['medium'][:10])
        sample.extend(by_severity['low'][:5])
        return sample

    elif sample_size == 'quick':  # 20 attacks
        # 2-3 per category
        categories = attack_engine.get_categories()
        sample = []
        for cat in categories:
            cat_attacks = attack_engine.get_attacks_by_category(cat)
            sorted_attacks = sorted(cat_attacks,
                                   key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.severity, 4))
            sample.extend(sorted_attacks[:3])
        return sample[:20]

    else:  # all
        return all_attacks


def get_defense_configurations():
    """Get all defense mechanisms"""
    guardian_client = LLMClientFactory.create(
        LLMProvider.OLLAMA,
        base_url=OLLAMA_BASE_URL,
        model=GUARDIAN_MODEL
    )

    return [
        ('NoDefense', None),
        ('InputSanitizer', InputSanitizer()),
        ('PromptTemplate', PromptTemplate()),
        ('OutputFilter', OutputFilter()),
        ('ContextIsolation', ContextIsolation()),
        ('InstructionHierarchy', InstructionHierarchy()),
        ('PerplexityFilter', PerplexityFilter()),
        ('SemanticSimilarity', SemanticSimilarity()),
        ('DualLLM', DualLLM({'guardian_client': guardian_client}))
    ]


def main():
    print("=" * 80)
    print("SAMPLE COMPARISON - Optimized for Slow PCs")
    print("=" * 80)

    # Load attacks
    print("\n1. Loading attacks...")
    attack_engine = AttackEngine()
    attack_engine.load_attacks()
    print(f"   ✓ Loaded {attack_engine.get_statistics()['total_attacks']} attacks")

    # Choose sample size
    print("\n2. Choose sample size:")
    print("   1. Balanced (40 attacks) - 5 per category - ~40 min - 90-95% confidence ⭐ RECOMMENDED")
    print("   2. Strategic (30 attacks) - By severity - ~30 min - 85-90% confidence")
    print("   3. Quick (20 attacks) - Fast test - ~20 min - 75-80% confidence")
    print("   4. All (84 attacks) - Full test - ~84 min - 100% confidence")

    choice = input("\n   Choice (1-4): ").strip()

    sample_map = {'1': 'balanced', '2': 'strategic', '3': 'quick', '4': 'all'}
    sample_type = sample_map.get(choice, 'balanced')

    attacks = get_sample_attacks(attack_engine, sample_type)
    print(f"\n   ✓ Selected {len(attacks)} attacks")

    # Get defenses
    print("\n3. Preparing defenses...")
    defenses = get_defense_configurations()
    print(f"   ✓ Testing {len(defenses)} defense configurations")

    # Setup database
    print("\n4. Database setup...")
    db = Database()
    db.create_tables()

    db_stats = db.get_statistics()
    if db_stats['total_tests'] > 0:
        print(f"   ⚠ Found {db_stats['total_tests']} existing tests")
        clear = input("   Clear previous results? (y/N): ")
        if clear.lower() == 'y':
            db.clear_all()
            print("   ✓ Database cleared")

    # Estimate
    total_tests = len(attacks) * len(defenses)
    est_time = (total_tests * 6) / 60

    print(f"\n5. Test Summary:")
    print(f"   Attacks: {len(attacks)}")
    print(f"   Defenses: {len(defenses)}")
    print(f"   Total tests: {total_tests}")
    print(f"   Estimated time: ~{est_time:.0f} minutes")

    proceed = input("\n   Proceed? (y/N): ")
    if proceed.lower() != 'y':
        print("   Cancelled.")
        return 0

    # Create LLM client
    print("\n6. Connecting to Ollama...")
    try:
        client = LLMClientFactory.create(
            LLMProvider.OLLAMA,
            base_url=OLLAMA_BASE_URL,
            model=DEFAULT_OLLAMA_MODEL
        )
        print("   ✓ Connected")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return 1

    # Run tests
    print("\n" + "=" * 80)
    print("RUNNING TESTS")
    print("=" * 80)

    eval_engine = EvaluationEngine(client, db)
    results = {}

    for defense_name, defense in defenses:
        print(f"\n{defense_name}")

        defense_results = []
        with tqdm(total=len(attacks), desc=f"  {defense_name:25s}", unit="attack") as pbar:
            for attack in attacks:
                try:
                    result = eval_engine.evaluate_attack(attack, defense)
                    defense_results.append(result)

                    successful = sum(1 for r in defense_results if r.attack_successful)
                    asr = (successful / len(defense_results)) * 100
                    pbar.set_postfix({'ASR': f"{asr:.1f}%"})
                    pbar.update(1)
                except Exception as e:
                    print(f"\n  ✗ Error: {e}")
                    pbar.update(1)

        results[defense_name] = defense_results

        # Show results
        if defense_results:
            successful = sum(1 for r in defense_results if r.attack_successful)
            asr = (successful / len(defense_results)) * 100
            der = 100 - asr
            print(f"  ASR: {asr:.2f}% | DER: {der:.2f}%")

    # Summary table
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    print(f"\n{'Defense':<30} {'Tests':<8} {'ASR':<10} {'DER':<10}")
    print("-" * 68)

    for defense_name, defense_results in results.items():
        if defense_results:
            successful = sum(1 for r in defense_results if r.attack_successful)
            asr = (successful / len(defense_results)) * 100
            der = 100 - asr

            print(
                f"{defense_name:<30} "
                f"{len(defense_results):<8} "
                f"{asr:>6.2f}%   "
                f"{der:>6.2f}%"
            )

    # Best defense
    best_defense = min(results.items(),
                      key=lambda x: sum(1 for r in x[1] if r.attack_successful) if x[1] else float('inf'))

    if best_defense[1]:
        best_asr = (sum(1 for r in best_defense[1] if r.attack_successful) / len(best_defense[1])) * 100
        best_der = 100 - best_asr

        print("\n" + "=" * 80)
        print(f"BEST DEFENSE: {best_defense[0]}")
        print(f"ASR: {best_asr:.2f}% | DER: {best_der:.2f}%")
        print("=" * 80)

    db.close()
    print("\n✓ Test complete!")

    return 0


if __name__ == '__main__':
    sys.exit(main())