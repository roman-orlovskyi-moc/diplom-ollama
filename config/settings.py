"""
Configuration management for the application
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

# ============================================================================
# MODEL NAME CONSTANTS
# ============================================================================
# These constants define the default model names for each provider.
# Update these constants to change the default models across the entire project.

# Ollama models (local)
DEFAULT_OLLAMA_MODEL = 'llama3.2'

# Guardian model
GUARDIAN_MODEL = 'llama3.2:1b'
# Other options: 'llama3.2', 'gemma3:1b'

# OpenAI models (API)
DEFAULT_OPENAI_MODEL = 'gpt-5-nano'

# Anthropic models (API)
DEFAULT_ANTHROPIC_MODEL = 'claude-haiku-4-5-20251001'

# Perplexity filter model (local, for defense mechanisms)
DEFAULT_PERPLEXITY_MODEL = 'distilgpt2'
# Other options: 'gpt2', 'distilgpt2' (faster), 'gpt2-medium'

# ============================================================================
# LLM CONFIGURATION
# ============================================================================
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'ollama')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://ollama:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', DEFAULT_OLLAMA_MODEL)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', DEFAULT_OPENAI_MODEL)
OPENAI_TPM_LIMIT = int(os.getenv('OPENAI_TPM_LIMIT', 200000))

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', DEFAULT_ANTHROPIC_MODEL)
ANTHROPIC_TPM_LIMIT = int(os.getenv('ANTHROPIC_TPM_LIMIT', 10000))

# Flask Configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key_change_me')

# Database Configuration
DATABASE_PATH = BASE_DIR / os.getenv('DATABASE_PATH', 'data/results/test_results.db')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = BASE_DIR / os.getenv('LOG_FILE', 'logs/app.log')

# Data Directories
ATTACKS_DIR = BASE_DIR / 'data/attacks'
RESULTS_DIR = BASE_DIR / 'data/results'
EXPORTS_DIR = BASE_DIR / 'data/exports'

# Ensure directories exist
ATTACKS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
