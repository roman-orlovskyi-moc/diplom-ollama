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

# OpenAI models (API)
DEFAULT_OPENAI_MODEL = 'gpt-4o'  # Latest GPT-4 Omni model
# Other options: 'gpt-4', 'gpt-4-turbo', 'o1-preview', 'o1-mini'

# Anthropic models (API)
DEFAULT_ANTHROPIC_MODEL = 'claude-sonnet-4-5-20250929'  # Claude Sonnet 4.5
# Other options: 'claude-3-5-sonnet-20241022', 'claude-3-opus-20240229'

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

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', DEFAULT_ANTHROPIC_MODEL)

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
