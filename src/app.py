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

# Configure Flask with correct template and static paths
template_dir = project_root / 'src' / 'web' / 'templates'
static_dir = project_root / 'src' / 'web' / 'static'

app = Flask(__name__,
            template_folder=str(template_dir),
            static_folder=str(static_dir))
app.config['SECRET_KEY'] = 'thesis_demo_key_2024'

# Initialize components
attack_engine = AttackEngine()
attack_engine.load_attacks()

llm_client = LLMClientFactory.create_from_env()
db = Database()
db.create_tables()  # Ensure database tables are created
eval_engine = EvaluationEngine(llm_client, db)

# Available defenses
DEFENSES = {
    'none': ('No Defense', None),
    'input_sanitizer': ('Input Sanitizer', InputSanitizer()),
    'prompt_template': ('Prompt Template', PromptTemplate()),
    'output_filter': ('Output Filter', OutputFilter()),
    'context_isolation': ('Context Isolation', ContextIsolation()),
}


@app.route('/')
def index():
    """Homepage"""
    stats = attack_engine.get_statistics()
    return render_template('index.html', stats=stats)


@app.route('/attacks')
def attacks():
    """Attack library page"""
    all_attacks = attack_engine.get_all_attacks()
    categories = attack_engine.get_categories()

    return render_template('attacks.html',
                         attacks=all_attacks,
                         categories=categories)


@app.route('/attack/<attack_id>')
def attack_detail(attack_id):
    """Single attack detail page"""
    attack = attack_engine.get_attack_by_id(attack_id)
    if not attack:
        return "Attack not found", 404

    return render_template('attack_detail.html', attack=attack)


@app.route('/demo')
def demo():
    """Interactive demo page"""
    attacks = attack_engine.get_all_attacks()
    return render_template('demo.html',
                         attacks=attacks,
                         defenses=DEFENSES)


@app.route('/api/test-attack', methods=['POST'])
def test_attack():
    """API endpoint to test an attack"""
    data = request.json
    attack_id = data.get('attack_id')
    defense_name = data.get('defense', 'none')

    attack = attack_engine.get_attack_by_id(attack_id)
    if not attack:
        return jsonify({'error': 'Attack not found'}), 404

    defense_label, defense = DEFENSES.get(defense_name, DEFENSES['none'])

    try:
        result = eval_engine.evaluate_attack(attack, defense)

        return jsonify({
            'success': True,
            'attack_id': result.attack_id,
            'attack_name': result.attack_name,
            'defense_name': result.defense_name,
            'attack_successful': result.attack_successful,
            'response': result.response,
            'latency_ms': result.latency_ms,
            'tokens_used': result.tokens_used,
            'cost': result.cost
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/comparison')
def comparison():
    """Defense comparison page"""
    return render_template('comparison.html', defenses=DEFENSES)


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


@app.route('/dashboard')
def dashboard():
    """Metrics dashboard"""
    db_stats = db.get_statistics()
    attack_stats = attack_engine.get_statistics()

    return render_template('dashboard.html',
                         db_stats=db_stats,
                         attack_stats=attack_stats)


@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    return jsonify(db.get_statistics())


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)