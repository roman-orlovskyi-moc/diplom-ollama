#!/usr/bin/env python3
"""
Focused Comparison - Test specific important scenarios

This script allows you to customize exactly what to test:
- Choose specific attack categories
- Choose specific defenses
- Choose specific models
- Set custom attack count per category

Perfect for:
- Testing specific hypotheses
- Comparing 2-3 promising defenses
- Budget-limited research
- Iterative defense development
- Category-specific analysis
"""
import sys
from pathlib import Path
from tqdm import tqdm
import json
import random
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
from src.defenses.dual_llm import DualLLM
from src.defenses.instruction_hierarchy import InstructionHierarchy
from config.settings import (
    OPENAI_API_KEY, ANTHROPIC_API_KEY,
    DEFAULT_OLLAMA_MODEL, DEFAULT_OPENAI_MODEL, DEFAULT_ANTHROPIC_MODEL
)


# ============================================================================
# CONFIGURATION - CUSTOMIZE YOUR TEST HERE
# ============================================================================

# Preset configurations for common scenarios
PRESETS = {
    'thesis_minimal': {
        'name': 'Minimal Thesis Test',
        'description': 'Absolute minimum for valid thesis results',
        'attacks_per_category': 3,
        'categories': None,  # All categories
        'defenses': ['NoDefense', 'InputSanitizer', 'PromptTemplate-XML', 'InstructionHierarchy'],
        'models': 'all',
        'estimated_tests': 60,
        'estimated_cost': '$2-4',
        'estimated_time': '8-12 min'
    },
    'defense_comparison': {
        'name': 'Defense Mechanism Comparison',
        'description': 'Compare top 3 defenses deeply',
        'attacks_per_category': 8,
        'categories': None,
        'defenses': ['NoDefense', 'PromptTemplate-XML', 'InstructionHierarchy', 'ContextIsolation'],
        'models': 'all',
        'estimated_tests': 192,
        'estimated_cost': '$5-10',
        'estimated_time': '20-30 min'
    },
    'category_specific': {
        'name': 'Category-Specific Analysis',
        'description': 'Deep dive into specific attack categories',
        'attacks_per_category': 10,
        'categories': ['jailbreak', 'role_confusion'],  # Most common
        'defenses': 'all_available',
        'models': 'all',
        'estimated_tests': 140,
        'estimated_cost': '$4-8',
        'estimated_time': '15-25 min'
    },
    'model_comparison': {
        'name': 'Model Vulnerability Comparison',
        'description': 'Compare model vulnerabilities with minimal defenses',
        'attacks_per_category': 5,
        'categories': None,
        'defenses': ['NoDefense', 'PromptTemplate-XML'],
        'models': 'all',
        'estimated_tests': 60,
        'estimated_cost': '$2-5',
        'estimated_time': '8-12 min'
    },
    'best_defense_validation': {
        'name': 'Validate Best Defense',
        'description': 'Deep test of your best defense candidate',
        'attacks_per_category': 15,
        'categories': None,
        'defenses': ['NoDefense', 'InstructionHierarchy'],  # Change to your best
        'models': 'all',
        'estimated_tests': 180,
        'estimated_cost': '$5-12',
        'estimated_time': '20-30 min'
    },
    'custom': {
        'name': 'Custom Configuration',
        'description': 'Manually configure all parameters',
        'attacks_per_category': None,  # Will prompt
        'categories': None,  # Will prompt
        'defenses': None,  # Will prompt
        'models': None,  # Will prompt
        'estimated_tests': 'varies',
        'estimated_cost': 'varies',
        'estimated_time': 'varies'
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_available_models():
    """Get all available models"""
    models = []

    models.append({
        'name': 'Llama3.2',
        'provider': LLMProvider.OLLAMA,
        'config': {'base_url': 'http://localhost:11434', 'model': DEFAULT_OLLAMA_MODEL}
    })

    if OPENAI_API_KEY:
        models.append({
            'name': 'GPT-4o',
            'provider': LLMProvider.OPENAI,
            'config': {'api_key': OPENAI_API_KEY, 'model': DEFAULT_OPENAI_MODEL}
        })

    if ANTHROPIC_API_KEY:
        models.append({
            'name': 'Claude-Sonnet-4.5',
            'provider': LLMProvider.ANTHROPIC,
            'config': {'api_key': ANTHROPIC_API_KEY, 'model': DEFAULT_ANTHROPIC_MODEL}
        })

    return models


def get_all_available_defenses():
    """Get all available defenses"""
    return {
        'NoDefense': None,
        'InputSanitizer': InputSanitizer(),
        'PromptTemplate-Delimited': PromptTemplate({'template_style': 'delimited'}),
        'PromptTemplate-XML': PromptTemplate({'template_style': 'xml'}),
        'OutputFilter': OutputFilter(),
        'ContextIsolation': ContextIsolation(),
        'InstructionHierarchy': InstructionHierarchy(),
    }


def select_preset():
    """Let user select a preset configuration"""
    print("\n" + "=" * 80)
    print("SELECT TEST CONFIGURATION")
    print("=" * 80)

    print("\nAvailable presets:")
    for i, (key, preset) in enumerate(PRESETS.items(), 1):
        print(f"\n{i}. {preset['name']}")
        print(f"   Description: {preset['description']}")
        print(f"   Estimated tests: {preset['estimated_tests']}")
        print(f"   Estimated cost: {preset['estimated_cost']}")
        print(f"   Estimated time: {preset['estimated_time']}")

    while True:
        choice = input("\nSelect preset (1-6): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(PRESETS):
                preset_key = list(PRESETS.keys())[idx]
                return preset_key, PRESETS[preset_key]
        except ValueError:
            pass
        print("Invalid choice. Please try again.")


def configure_custom(attack_engine, all_models):
    """Configure custom test parameters"""
    config = {}

    # Select models
    print("\n1. SELECT MODELS:")
    print("   Available models:")
    for i, model in enumerate(all_models, 1):
        print(f"   {i}. {model['name']}")
    print(f"   {len(all_models)+1}. All models")

    model_choice = input(f"\n   Select models (comma-separated numbers or 'all'): ").strip()

    if model_choice.lower() == 'all' or str(len(all_models)+1) in model_choice:
        config['models'] = all_models
    else:
        indices = [int(i)-1 for i in model_choice.split(',')]
        config['models'] = [all_models[i] for i in indices if 0 <= i < len(all_models)]

    # Select categories
    print("\n2. SELECT ATTACK CATEGORIES:")
    categories = attack_engine.get_categories()
    for i, cat in enumerate(categories, 1):
        stats = attack_engine.get_attacks_by_category(cat)
        print(f"   {i}. {cat} ({len(stats)} attacks)")
    print(f"   {len(categories)+1}. All categories")

    cat_choice = input(f"\n   Select categories (comma-separated numbers or 'all'): ").strip()

    if cat_choice.lower() == 'all' or str(len(categories)+1) in cat_choice:
        config['categories'] = None
    else:
        indices = [int(i)-1 for i in cat_choice.split(',')]
        config['categories'] = [categories[i] for i in indices if 0 <= i < len(categories)]

    # Attacks per category
    attacks_per = input("\n3. ATTACKS PER CATEGORY (3-20): ").strip()
    config['attacks_per_category'] = int(attacks_per)

    # Select defenses
    print("\n4. SELECT DEFENSES:")
    all_defenses = get_all_available_defenses()
    for i, name in enumerate(all_defenses.keys(), 1):
        print(f"   {i}. {name}")
    print(f"   {len(all_defenses)+1}. All defenses")

    def_choice = input(f"\n   Select defenses (comma-separated numbers or 'all'): ").strip()

    if def_choice.lower() == 'all' or str(len(all_defenses)+1) in def_choice:
        config['defenses'] = list(all_defenses.keys())
    else:
        indices = [int(i)-1 for i in def_choice.split(',')]
        defense_names = list(all_defenses.keys())
        config['defenses'] = [defense_names[i] for i in indices if 0 <= i < len(defense_names)]

    return config


def sample_attacks(attack_engine, n_per_category, selected_categories=None):
    """Sample n attacks from each category"""
    sampled = []

    categories = selected_categories if selected_categories else attack_engine.get_categories()

    for category in categories:
        cat_attacks = attack_engine.get_attacks_by_category(category)
        n_sample = min(n_per_category, len(cat_attacks))
        sampled.extend(random.sample(cat_attacks, n_sample))
        print(f"   {category}: {n_sample} attacks")

    return sampled


def calculate_asr_der(results):
    """Calculate ASR and DER"""
    if not results:
        return 0.0, 0.0
    total = len(results)
    successful = sum(1 for r in results if r.attack_successful)
    asr = (successful / total) * 100
    der = 100 - asr
    return asr, der


def print_section(title):
    print("\n" + "=" * 80)
    print(f"{title.center(80)}")
    print("=" * 80)


def export_results(all_results, config_name, output_dir):
    """Export results"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'focused_comparison_{config_name}_{timestamp}'

    # CSV
    csv_path = output_dir / f'{filename}.csv'
    with open(csv_path, 'w') as f:
        f.write('Model,Defense,Tests,Successful,ASR(%),DER(%),Avg_Latency_ms,Total_Cost\n')

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

    print(f"✓ CSV: {csv_path}")

    # JSON
    json_path = output_dir / f'{filename}.json'
    with open(json_path, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'configuration': config_name,
            'results': {
                model_name: {
                    defense_name: {
                        'tests': len(results),
                        'asr': calculate_asr_der(results)[0],
                        'der': calculate_asr_der(results)[1]
                    }
                    for defense_name, results in model_results.items() if results
                }
                for model_name, model_results in all_results.items()
            }
        }, f, indent=2)

    print(f"✓ JSON: {json_path}")

    return csv_path, json_path


def print_results_table(all_results):
    """Print comparison table"""
    print_section("RESULTS")

    print(f"\n{'Model':<20} {'Defense':<25} {'Tests':<7} {'ASR (%)':<10} {'DER (%)'}")
    print("-" * 75)

    for model_name, model_results in all_results.items():
        for defense_name, results in model_results.items():
            if results:
                asr, der = calculate_asr_der(results)
                print(f"{model_name:<20} {defense_name:<25} {len(results):<7} {asr:>6.2f}%   {der:>6.2f}%")


def print_conclusions(all_results):
    """Print focused conclusions"""
    print_section("CONCLUSIONS")

    # Best defense
    print("\n🏆 BEST DEFENSE:")
    defense_scores = {}
    for model_name, model_results in all_results.items():
        for defense_name, results in model_results.items():
            if results and defense_name != 'NoDefense':
                asr, der = calculate_asr_der(results)
                if defense_name not in defense_scores:
                    defense_scores[defense_name] = []
                defense_scores[defense_name].append(der)

    if defense_scores:
        best = max(defense_scores.items(), key=lambda x: sum(x[1])/len(x[1]))
        print(f"   {best[0]}: {sum(best[1])/len(best[1]):.2f}% average DER")

    # Per model
    print("\n📱 BEST DEFENSE PER MODEL:")
    for model_name, model_results in all_results.items():
        best_defense = max(
            [(name, results) for name, results in model_results.items()
             if results and name != 'NoDefense'],
            key=lambda x: calculate_asr_der(x[1])[1],
            default=(None, None)
        )
        if best_defense[0]:
            der = calculate_asr_der(best_defense[1])[1]
            print(f"   {model_name}: {best_defense[0]} ({der:.2f}% DER)")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run focused comparison"""
    print_section("FOCUSED COMPARISON - CUSTOMIZED TESTING")

    # Check models
    all_models = get_all_available_models()
    print(f"\n✓ Available models: {', '.join(m['name'] for m in all_models)}")

    # Load attacks
    attack_engine = AttackEngine()
    attack_engine.load_attacks()
    print(f"✓ Loaded attacks from {len(attack_engine.get_categories())} categories")

    # Select configuration
    preset_key, preset = select_preset()

    if preset_key == 'custom':
        config = configure_custom(attack_engine, all_models)
    else:
        # Use preset
        config = {}

        # Models
        if preset['models'] == 'all':
            config['models'] = all_models
        else:
            config['models'] = all_models  # Presets use all by default

        # Categories
        config['categories'] = preset['categories']

        # Attacks per category
        config['attacks_per_category'] = preset['attacks_per_category']

        # Defenses
        all_defenses = get_all_available_defenses()
        if preset['defenses'] == 'all_available':
            config['defenses'] = list(all_defenses.keys())
        else:
            config['defenses'] = preset['defenses']

    # Sample attacks
    print(f"\n📊 Sampling attacks ({config['attacks_per_category']} per category):")
    attacks = sample_attacks(attack_engine, config['attacks_per_category'],
                            config['categories'])
    print(f"\n✓ Selected {len(attacks)} attacks")

    # Get defense objects
    all_def_objects = get_all_available_defenses()
    defenses = [(name, all_def_objects[name]) for name in config['defenses']]

    # Calculate totals
    total_tests = len(attacks) * len(defenses) * len(config['models'])
    estimated_time_min = (total_tests * 3) / 60

    print(f"\n📈 TEST SUMMARY:")
    print(f"   Models: {len(config['models'])}")
    print(f"   Defenses: {len(defenses)}")
    print(f"   Attacks: {len(attacks)}")
    print(f"   Total tests: {total_tests}")
    print(f"   Estimated time: ~{estimated_time_min:.1f} minutes")

    proceed = input("\n   Proceed? (y/N): ")
    if proceed.lower() != 'y':
        return 0

    # Setup database
    db = Database()
    db.create_tables()

    # Run tests
    print_section("RUNNING FOCUSED TESTS")

    all_results = {}

    for model_info in config['models']:
        model_name = model_info['name']
        print(f"\n\n📱 {model_name}")
        print("-" * 80)

        try:
            client = LLMClientFactory.create(model_info['provider'], **model_info['config'])
            print(f"✓ Connected")
        except Exception as e:
            print(f"✗ Error: {e}")
            continue

        eval_engine = EvaluationEngine(client, db)
        model_results = {}

        for defense_name, defense in defenses:
            results = []

            with tqdm(total=len(attacks), desc=f"  {defense_name:25s}", unit="test") as pbar:
                for attack in attacks:
                    try:
                        result = eval_engine.evaluate_attack(attack, defense)
                        results.append(result)

                        asr, _ = calculate_asr_der(results)
                        pbar.set_postfix({'ASR': f"{asr:.1f}%"})
                        pbar.update(1)
                    except Exception as e:
                        pbar.update(1)

            model_results[defense_name] = results

            if results:
                asr, der = calculate_asr_der(results)
                print(f"    ASR: {asr:.2f}% | DER: {der:.2f}%")

        all_results[model_name] = model_results

    # Results
    print_results_table(all_results)

    # Export
    print_section("EXPORTING")
    csv_path, json_path = export_results(all_results, preset_key,
                                         Path('data/exports'))

    # Conclusions
    print_conclusions(all_results)

    # Done
    print_section("FOCUSED COMPARISON COMPLETE")

    print("\n✓ Testing complete!")
    print(f"\n📁 Output files:")
    print(f"   • {csv_path}")
    print(f"   • {json_path}")

    print("\n💡 NEXT STEPS:")
    print("   • Review results for your specific scenario")
    print("   • Run additional focused tests as needed")
    print("   • Combine with full comparison for comprehensive thesis")

    db.close()
    return 0


if __name__ == '__main__':
    random.seed(42)
    sys.exit(main())