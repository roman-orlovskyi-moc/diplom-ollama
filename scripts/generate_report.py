#!/usr/bin/env python3
"""
Generate Report - Create visualizations and analysis
"""
import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import Database
from src.core.evaluation import EvaluationEngine


def generate_summary_stats(db: Database):
    """Generate summary statistics"""
    print("\nGenerating summary statistics...")

    stats = db.get_statistics()

    summary = {
        'total_tests': stats['total_tests'],
        'successful_attacks': stats['successful_attacks'],
        'overall_success_rate': stats['successful_attacks'] / stats['total_tests'] if stats['total_tests'] > 0 else 0,
        'by_defense': stats['by_defense'],
        'by_category': stats['by_category']
    }

    # Save to JSON
    output_path = Path('data/exports/summary_statistics.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"  ✓ Saved to {output_path}")

    return summary


def generate_comparison_table(db: Database):
    """Generate defense comparison table"""
    print("\nGenerating defense comparison table...")

    stats = db.get_statistics()
    defenses = stats.get('by_defense', {})

    # Create markdown table
    output_path = Path('data/exports/defense_comparison.md')

    with open(output_path, 'w') as f:
        f.write("# Defense Mechanism Comparison\n\n")
        f.write("| Defense | Total Tests | Successful Attacks | Attack Success Rate | Defense Effectiveness |\n")
        f.write("|---------|-------------|-------------------|---------------------|----------------------|\n")

        for defense_name, defense_stats in sorted(defenses.items(), key=lambda x: x[1]['success_rate']):
            total = defense_stats['total']
            successful = defense_stats['successful']
            success_rate = defense_stats['success_rate']
            effectiveness = 1 - success_rate

            f.write(
                f"| {defense_name} | {total} | {successful} | "
                f"{success_rate*100:.1f}% | {effectiveness*100:.1f}% |\n"
            )

    print(f"  ✓ Saved to {output_path}")


def generate_category_analysis(db: Database):
    """Generate category-wise analysis"""
    print("\nGenerating category analysis...")

    stats = db.get_statistics()
    categories = stats.get('by_category', {})

    output_path = Path('data/exports/category_analysis.md')

    with open(output_path, 'w') as f:
        f.write("# Attack Category Analysis\n\n")

        for category, cat_stats in sorted(categories.items(), key=lambda x: -x[1]['success_rate']):
            total = cat_stats['total']
            successful = cat_stats['successful']
            success_rate = cat_stats['success_rate']

            f.write(f"## {category.replace('_', ' ').title()}\n\n")
            f.write(f"- Total tests: {total}\n")
            f.write(f"- Successful attacks: {successful}\n")
            f.write(f"- Success rate: {success_rate*100:.1f}%\n\n")

            # Get results for this category
            results = db.get_results_by_category(category)

            # Group by defense
            by_defense = {}
            for result in results:
                defense = result.defense_name
                if defense not in by_defense:
                    by_defense[defense] = {'total': 0, 'successful': 0}
                by_defense[defense]['total'] += 1
                if result.attack_successful:
                    by_defense[defense]['successful'] += 1

            f.write("### By Defense Mechanism\n\n")
            f.write("| Defense | Success Rate |\n")
            f.write("|---------|-------------|\n")

            for defense, d_stats in sorted(by_defense.items(), key=lambda x: x[1]['successful']/x[1]['total'] if x[1]['total'] > 0 else 0):
                rate = d_stats['successful'] / d_stats['total'] if d_stats['total'] > 0 else 0
                f.write(f"| {defense} | {rate*100:.1f}% |\n")

            f.write("\n---\n\n")

    print(f"  ✓ Saved to {output_path}")


def generate_defense_per_model_report(db: Database):
    """Generate report on best defense per model"""
    print("\nGenerating defense per model report...")

    # Get all results
    all_results = db.get_all_results()
    if not all_results:
        print("  ⚠ No results found")
        return

    # Group results by model
    by_model = {}
    for result in all_results:
        model = result.model
        if model not in by_model:
            by_model[model] = {}

        defense = result.defense_name
        if defense not in by_model[model]:
            by_model[model][defense] = {'total': 0, 'successful': 0}

        by_model[model][defense]['total'] += 1
        if result.attack_successful:
            by_model[model][defense]['successful'] += 1

    # Create markdown report
    output_path = Path('data/exports/best_defense_per_model.md')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write("# Best Defense Mechanism Per Model\n\n")
        f.write("This report shows the most effective defense for each model.\n\n")

        for model, defenses in sorted(by_model.items()):
            f.write(f"## {model}\n\n")

            # Calculate success rates for each defense
            defense_stats = []
            for defense, stats in defenses.items():
                success_rate = (stats['successful'] / stats['total']) if stats['total'] > 0 else 0
                effectiveness = 1 - success_rate
                defense_stats.append({
                    'name': defense,
                    'total': stats['total'],
                    'successful': stats['successful'],
                    'success_rate': success_rate,
                    'effectiveness': effectiveness
                })

            # Sort by effectiveness (best first)
            defense_stats.sort(key=lambda x: x['effectiveness'], reverse=True)

            # Write table
            f.write("| Defense | Total Tests | Successful Attacks | ASR | DER |\n")
            f.write("|---------|-------------|-------------------|-----|-----|\n")

            for d_stat in defense_stats:
                f.write(
                    f"| {d_stat['name']} | {d_stat['total']} | {d_stat['successful']} | "
                    f"{d_stat['success_rate']*100:.1f}% | {d_stat['effectiveness']*100:.1f}% |\n"
                )

            # Highlight best defense
            if defense_stats:
                best = defense_stats[0]
                f.write(f"\n**Best Defense:** {best['name']} with {best['effectiveness']*100:.1f}% effectiveness\n\n")

            f.write("---\n\n")

    print(f"  ✓ Saved to {output_path}")


def generate_attack_success_per_model_report(db: Database):
    """Generate report on most successful attacks by model (not category)"""
    print("\nGenerating most successful attacks per model report...")

    # Get all results
    all_results = db.get_all_results()
    if not all_results:
        print("  ⚠ No results found")
        return

    # Group results by model and attack name
    by_model = {}
    for result in all_results:
        model = result.model
        if model not in by_model:
            by_model[model] = {}

        attack_name = result.attack_name
        if attack_name not in by_model[model]:
            by_model[model][attack_name] = {
                'total': 0,
                'successful': 0,
                'category': result.attack_category,
                'severity': result.attack_severity
            }

        by_model[model][attack_name]['total'] += 1
        if result.attack_successful:
            by_model[model][attack_name]['successful'] += 1

    # Create markdown report
    output_path = Path('data/exports/most_successful_attacks_per_model.md')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write("# Most Successful Attacks Per Model\n\n")
        f.write("This report shows the top attacks by success rate for each model.\n\n")

        for model, attacks in sorted(by_model.items()):
            f.write(f"## {model}\n\n")

            # Calculate success rates for each attack
            attack_stats = []
            for attack_name, stats in attacks.items():
                success_rate = (stats['successful'] / stats['total']) if stats['total'] > 0 else 0
                attack_stats.append({
                    'name': attack_name,
                    'category': stats['category'],
                    'severity': stats['severity'],
                    'total': stats['total'],
                    'successful': stats['successful'],
                    'success_rate': success_rate
                })

            # Sort by success rate (highest first)
            attack_stats.sort(key=lambda x: (-x['success_rate'], -x['successful']))

            # Write table for top 10 attacks
            f.write("### Top 10 Most Successful Attacks\n\n")
            f.write("| Attack Name | Category | Severity | Success Rate | Successful/Total |\n")
            f.write("|-------------|----------|----------|--------------|------------------|\n")

            for a_stat in attack_stats[:10]:
                f.write(
                    f"| {a_stat['name']} | {a_stat['category']} | {a_stat['severity']} | "
                    f"{a_stat['success_rate']*100:.1f}% | {a_stat['successful']}/{a_stat['total']} |\n"
                )

            f.write("\n---\n\n")

    print(f"  ✓ Saved to {output_path}")


def generate_visualizations(db: Database):
    """Generate visualizations using matplotlib"""
    print("\nGenerating visualizations...")

    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
    except ImportError:
        print("  ⚠ matplotlib not installed, skipping visualizations")
        print("  Install with: pip install matplotlib")
        return

    stats = db.get_statistics()
    viz_dir = Path('data/exports/visualizations')
    viz_dir.mkdir(parents=True, exist_ok=True)

    # 1. Defense Effectiveness Bar Chart
    defenses = stats.get('by_defense', {})
    if defenses:
        defense_names = list(defenses.keys())
        effectiveness_rates = [1 - d['success_rate'] for d in defenses.values()]

        plt.figure(figsize=(10, 6))
        plt.bar(defense_names, [e*100 for e in effectiveness_rates])
        plt.xlabel('Defense Mechanism')
        plt.ylabel('Defense Effectiveness Rate (%)')
        plt.title('Defense Mechanism Effectiveness Comparison')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(viz_dir / 'defense_effectiveness.png', dpi=300)
        plt.close()
        print(f"  ✓ Created defense_effectiveness.png")

    # 2. Category Success Rates
    categories = stats.get('by_category', {})
    if categories:
        cat_names = list(categories.keys())
        success_rates = [c['success_rate']*100 for c in categories.values()]

        plt.figure(figsize=(10, 6))
        plt.bar(cat_names, success_rates)
        plt.xlabel('Attack Category')
        plt.ylabel('Attack Success Rate (%)')
        plt.title('Attack Success Rate by Category')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(viz_dir / 'category_success_rates.png', dpi=300)
        plt.close()
        print(f"  ✓ Created category_success_rates.png")

    # 3. Heatmap of Defense vs Category
    # Get all unique defenses and categories
    all_results = db.get_all_results()
    if all_results:
        import numpy as np

        defense_list = sorted(list(set(r.defense_name for r in all_results)))
        category_list = sorted(list(set(r.attack_category for r in all_results)))

        # Create matrix
        matrix = np.zeros((len(defense_list), len(category_list)))

        for i, defense in enumerate(defense_list):
            for j, category in enumerate(category_list):
                # Get success rate for this combination
                relevant = [r for r in all_results
                           if r.defense_name == defense and r.attack_category == category]
                if relevant:
                    success_count = sum(1 for r in relevant if r.attack_successful)
                    matrix[i, j] = (success_count / len(relevant)) * 100

        plt.figure(figsize=(12, 8))
        plt.imshow(matrix, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=100)
        plt.colorbar(label='Attack Success Rate (%)')
        plt.xticks(range(len(category_list)), category_list, rotation=45, ha='right')
        plt.yticks(range(len(defense_list)), defense_list)
        plt.xlabel('Attack Category')
        plt.ylabel('Defense Mechanism')
        plt.title('Attack Success Rate Heatmap: Defense vs Category')
        plt.tight_layout()
        plt.savefig(viz_dir / 'heatmap_defense_category.png', dpi=300)
        plt.close()
        print(f"  ✓ Created heatmap_defense_category.png")

    print(f"\n  All visualizations saved to {viz_dir}/")


def main():
    """Generate comprehensive report"""
    print("=" * 80)
    print("REPORT GENERATION")
    print("=" * 80)

    # Initialize database
    db = Database()

    # Check if there are results
    stats = db.get_statistics()
    if stats['total_tests'] == 0:
        print("\n✗ No test results found in database.")
        print("  Run experiments first: python scripts/run_experiments.py")
        return 1

    print(f"\nFound {stats['total_tests']} test results in database")

    # Generate reports
    print("\n" + "=" * 80)
    summary = generate_summary_stats(db)
    generate_comparison_table(db)
    generate_category_analysis(db)
    generate_defense_per_model_report(db)
    generate_attack_success_per_model_report(db)
    generate_visualizations(db)

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal tests: {summary['total_tests']}")
    print(f"Successful attacks: {summary['successful_attacks']}")
    print(f"Overall success rate: {summary['overall_success_rate']*100:.1f}%")

    print("\nTop 3 Most Effective Defenses:")
    defenses_sorted = sorted(
        summary['by_defense'].items(),
        key=lambda x: x[1]['success_rate']
    )[:3]

    for i, (defense, stats) in enumerate(defenses_sorted, 1):
        effectiveness = (1 - stats['success_rate']) * 100
        print(f"  {i}. {defense}: {effectiveness:.1f}% effective")

    print("\nMost Vulnerable Categories:")
    categories_sorted = sorted(
        summary['by_category'].items(),
        key=lambda x: -x[1]['success_rate']
    )[:3]

    for i, (category, stats) in enumerate(categories_sorted, 1):
        print(f"  {i}. {category}: {stats['success_rate']*100:.1f}% success rate")

    print("\n" + "=" * 80)
    print("REPORT COMPLETE!")
    print("=" * 80)
    print("\nGenerated files:")
    print("  - data/exports/summary_statistics.json")
    print("  - data/exports/defense_comparison.md")
    print("  - data/exports/category_analysis.md")
    print("  - data/exports/best_defense_per_model.md")
    print("  - data/exports/most_successful_attacks_per_model.md")
    print("  - data/exports/experiment_results.csv")
    print("  - data/exports/visualizations/*.png")

    db.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())