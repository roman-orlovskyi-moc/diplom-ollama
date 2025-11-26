"""
Flask Web Application - Interactive Prompt Injection Testing Interface
"""
from flask import Flask, render_template, request, jsonify
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.attack_engine import AttackEngine
from src.core.llm_client import LLMClientFactory
from src.core.evaluation import EvaluationEngine
from src.utils.database import Database
from src.defenses.input_sanitizer import InputSanitizer
from src.defenses.prompt_template import PromptTemplate
from src.defenses.output_filter import OutputFilter
from src.defenses.context_isolation import ContextIsolation
from src.defenses.dual_llm import DualLLM
from src.defenses.instruction_hierarchy import InstructionHierarchy
from config.settings import (LLM_PROVIDER)

# Try to import ML-based defenses (optional dependencies)
try:
    from src.defenses.perplexity_filter import PerplexityFilter
    PERPLEXITY_AVAILABLE = True
except ImportError:
    PERPLEXITY_AVAILABLE = False
    PerplexityFilter = None

try:
    from src.defenses.semantic_similarity import SemanticSimilarity
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    SemanticSimilarity = None

# Configure Flask with correct template and static paths
template_dir = project_root / 'src' / 'web' / 'templates'
static_dir = project_root / 'src' / 'web' / 'static'

app = Flask(__name__,
            template_folder=str(template_dir),
            static_folder=str(static_dir))
app.config['SECRET_KEY'] = 'thesis_demo_key'

# Initialize components
attack_engine = AttackEngine()
attack_engine.load_attacks()

llm_client = LLMClientFactory.create_from_env()
db = Database()
db.create_tables()  # Ensure database tables are created
eval_engine = EvaluationEngine(llm_client, db)

# Available defenses - Build dynamically based on what's available
DEFENSES = {
    'none': ('No Defense', None),
    'input_sanitizer': ('Input Sanitizer', InputSanitizer()),
    'prompt_template': ('Prompt Template', PromptTemplate()),
    'output_filter': ('Output Filter', OutputFilter()),
    'context_isolation': ('Context Isolation', ContextIsolation()),
    'instruction_hierarchy': ('Instruction Hierarchy', InstructionHierarchy()),
}

# Add ML-based defenses if available
if PERPLEXITY_AVAILABLE and PerplexityFilter:
    DEFENSES['perplexity_filter'] = ('Perplexity Filter (ML)', PerplexityFilter())

if SEMANTIC_AVAILABLE and SemanticSimilarity:
    DEFENSES['semantic_similarity'] = ('Semantic Similarity (ML)', SemanticSimilarity())


@app.route('/')
def index():
    """Homepage"""
    db_stats = db.get_statistics()
    attack_stats = attack_engine.get_statistics()

    return render_template('index.html',
                            llm_provider=LLM_PROVIDER,
                            db_stats=db_stats,
                            attack_stats=attack_stats,
                            defenses=DEFENSES)


@app.route('/comparison')
def comparison():
    """Defense comparison page"""
    all_attacks = attack_engine.get_all_attacks()
    return render_template('comparison.html',
                            llm_provider=LLM_PROVIDER,
                            defenses=DEFENSES,
                            attacks=all_attacks)


@app.route('/api/compare-defenses', methods=['POST'])
def compare_defenses():
    """API endpoint to compare multiple defenses"""
    data = request.json
    attack_id = data.get('attack_id')

    attack = attack_engine.get_attack_by_id(attack_id)
    if not attack:
        return jsonify({'error': 'Attack not found'}), 404

    results = []
    for defense_key, (defense_label, defense) in DEFENSES.items():
        try:
            result = eval_engine.evaluate_attack(attack, defense)
            results.append({
                'defense_key': defense_key,
                'defense_name': defense_label,
                'attack_successful': result.attack_successful,
                'response': result.response,
                'latency_ms': result.latency_ms
            })
        except Exception as e:
            results.append({
                'defense_key': defense_key,
                'defense_name': defense_label,
                'error': str(e)
            })

    return jsonify({'results': results})


@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    return jsonify(db.get_statistics())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)