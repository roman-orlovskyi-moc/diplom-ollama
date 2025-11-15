#!/usr/bin/env python3
"""
Test Setup - Verify installation and configuration
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")

    try:
        from src.models.attack import Attack
        print("✓ Attack model")
    except Exception as e:
        print(f"✗ Attack model: {e}")
        return False

    try:
        from src.models.test_result import TestResult
        print("✓ TestResult model")
    except Exception as e:
        print(f"✗ TestResult model: {e}")
        return False

    try:
        from src.core.attack_engine import AttackEngine
        print("✓ AttackEngine")
    except Exception as e:
        print(f"✗ AttackEngine: {e}")
        return False

    try:
        from src.core.evaluation import EvaluationEngine
        print("✓ EvaluationEngine")
    except Exception as e:
        print(f"✗ EvaluationEngine: {e}")
        return False

    try:
        from src.core.llm_client import LLMClientFactory, LLMProvider
        print("✓ LLM Client")
    except Exception as e:
        print(f"✗ LLM Client: {e}")
        return False

    try:
        from src.defenses.input_sanitizer import InputSanitizer
        from src.defenses.prompt_template import PromptTemplate
        from src.defenses.output_filter import OutputFilter
        from src.defenses.context_isolation import ContextIsolation
        from src.defenses.dual_llm import DualLLM
        print("✓ All defense mechanisms")
    except Exception as e:
        print(f"✗ Defense mechanisms: {e}")
        return False

    try:
        from src.utils.database import Database
        print("✓ Database utilities")
    except Exception as e:
        print(f"✗ Database utilities: {e}")
        return False

    return True


def test_attack_loading():
    """Test loading attack patterns"""
    print("\nTesting attack pattern loading...")

    try:
        from src.core.attack_engine import AttackEngine

        engine = AttackEngine()
        count = engine.load_attacks()

        print(f"✓ Loaded {count} attack patterns")
        print(f"  Categories: {', '.join(engine.get_categories())}")

        stats = engine.get_statistics()
        print(f"  Severity distribution:")
        for severity, count in stats['severity_distribution'].items():
            print(f"    {severity}: {count}")

        return True
    except Exception as e:
        print(f"✗ Attack loading failed: {e}")
        return False


def test_llm_client():
    """Test LLM client connection"""
    print("\nTesting LLM client...")

    try:
        from src.core.llm_client import LLMClientFactory, LLMProvider

        # Try Ollama first (free/local)
        print("  Testing Ollama connection...")
        client = LLMClientFactory.create_from_env()

        result = client.generate(
            prompt="Say 'Hello' and nothing else.",
            system_prompt="You are a helpful assistant.",
            max_tokens=50
        )

        if 'error' in result:
            print(f"  ⚠ Ollama not available: {result['error']}")
            print("  Run: ollama pull llama3.2")
            return False
        else:
            print(f"  ✓ Ollama working (model: {result['model']})")
            print(f"    Response: {result['response'][:50]}...")
            return True

    except Exception as e:
        print(f"  ✗ LLM client test failed: {e}")
        return False


def test_database():
    """Test database operations"""
    print("\nTesting database...")

    try:
        from src.utils.database import Database
        from config.settings import BASE_DIR

        # Use temporary database for testing
        test_db_path = BASE_DIR / 'data/results/test_db.db'
        test_db_path.unlink(missing_ok=True)

        db = Database(test_db_path)
        db.create_tables()
        print("  ✓ Database tables created")

        # Clean up
        db.close()
        test_db_path.unlink(missing_ok=True)

        return True
    except Exception as e:
        print(f"  ✗ Database test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Project Setup")
    print("=" * 60)

    all_passed = True

    # Test imports
    if not test_imports():
        all_passed = False

    # Test attack loading
    if not test_attack_loading():
        all_passed = False

    # Test LLM client
    if not test_llm_client():
        all_passed = False
        print("\n  NOTE: Install Ollama to use local LLM:")
        print("  curl -fsSL https://ollama.com/install.sh | sh")
        print("  ollama pull llama3.2")

    # Test database
    if not test_database():
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! Setup is complete.")
    else:
        print("⚠ Some tests failed. Check errors above.")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())