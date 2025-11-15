#!/usr/bin/env python3
"""
Simple Test - Run a single attack with and without defense
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.attack_engine import AttackEngine
from src.core.llm_client import LLMClientFactory, LLMProvider
from src.core.evaluation import EvaluationEngine
from src.defenses.input_sanitizer import InputSanitizer
from src.defenses.prompt_template import PromptTemplate


def main():
    """Run simple test"""
    print("=" * 70)
    print("Simple Attack Test - Comparing Defense Mechanisms")
    print("=" * 70)

    # Load attacks
    print("\n1. Loading attack patterns...")
    attack_engine = AttackEngine()
    count = attack_engine.load_attacks()
    print(f"   Loaded {count} attacks")

    # Get a sample attack
    attack = attack_engine.get_attack_by_id('di_001')
    if not attack:
        print("   Error: Could not find attack 'di_001'")
        return 1

    print(f"\n2. Testing attack: {attack.name}")
    print(f"   Category: {attack.category}")
    print(f"   Severity: {attack.severity}")
    print(f"   Description: {attack.description}")

    # Create LLM client
    print("\n3. Initializing LLM client...")
    try:
        client = LLMClientFactory.create_from_env()
        print("   ✓ Ollama client ready")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return 1

    # Create evaluation engine
    eval_engine = EvaluationEngine(client)

    # Test without defense
    print("\n4. Running attack WITHOUT defense...")
    print(f"   System: {attack.context.system_prompt[:60]}...")
    print(f"   User: {attack.context.user_message[:60]}...")

    result_no_defense = eval_engine.evaluate_attack(attack, defense=None)

    print(f"\n   Result:")
    print(f"   - Attack successful: {result_no_defense.attack_successful}")
    print(f"   - Latency: {result_no_defense.latency_ms}ms")
    print(f"   - Response: {result_no_defense.response[:200]}...")

    # Test with Input Sanitizer
    print("\n5. Running attack WITH InputSanitizer defense...")
    defense = InputSanitizer()
    result_with_sanitizer = eval_engine.evaluate_attack(attack, defense=defense)

    print(f"\n   Result:")
    print(f"   - Attack successful: {result_with_sanitizer.attack_successful}")
    print(f"   - Latency: {result_with_sanitizer.latency_ms}ms")
    print(f"   - Response: {result_with_sanitizer.response[:200]}...")

    # Test with Prompt Template
    print("\n6. Running attack WITH PromptTemplate defense...")
    defense = PromptTemplate()
    result_with_template = eval_engine.evaluate_attack(attack, defense=defense)

    print(f"\n   Result:")
    print(f"   - Attack successful: {result_with_template.attack_successful}")
    print(f"   - Latency: {result_with_template.latency_ms}ms")
    print(f"   - Response: {result_with_template.response[:200]}...")

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Attack: {attack.name}")
    print(f"\nNo Defense:        Attack {'SUCCEEDED' if result_no_defense.attack_successful else 'BLOCKED'}")
    print(f"InputSanitizer:    Attack {'SUCCEEDED' if result_with_sanitizer.attack_successful else 'BLOCKED'}")
    print(f"PromptTemplate:    Attack {'SUCCEEDED' if result_with_template.attack_successful else 'BLOCKED'}")

    print("\nDefense effectiveness:")
    if not result_no_defense.attack_successful:
        print("  Note: Attack failed even without defense. LLM may have built-in protections.")
    else:
        if not result_with_sanitizer.attack_successful:
            print("  ✓ InputSanitizer successfully blocked the attack")
        else:
            print("  ✗ InputSanitizer failed to block the attack")

        if not result_with_template.attack_successful:
            print("  ✓ PromptTemplate successfully blocked the attack")
        else:
            print("  ✗ PromptTemplate failed to block the attack")

    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())