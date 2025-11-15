"""
Attack Engine - Loads and manages attack patterns
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from src.models.attack import Attack
from config.settings import ATTACKS_DIR


class AttackEngine:
    """Manages loading and categorizing attack patterns"""

    def __init__(self, attacks_dir: Path = None):
        self.attacks_dir = attacks_dir or ATTACKS_DIR
        self.attacks: List[Attack] = []
        self.attacks_by_category: Dict[str, List[Attack]] = {}
        self.attacks_by_id: Dict[str, Attack] = {}

    def load_attacks(self) -> int:
        """
        Load all attack patterns from JSON files

        Returns:
            Number of attacks loaded
        """
        self.attacks.clear()
        self.attacks_by_category.clear()
        self.attacks_by_id.clear()

        if not self.attacks_dir.exists():
            raise FileNotFoundError(f"Attacks directory not found: {self.attacks_dir}")

        # Load all JSON files
        for json_file in self.attacks_dir.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                category = data.get('category', 'unknown')
                attack_list = data.get('attacks', [])

                # Parse each attack
                for attack_data in attack_list:
                    attack = Attack.from_dict(attack_data, category)
                    self.attacks.append(attack)
                    self.attacks_by_id[attack.id] = attack

                    # Group by category
                    if category not in self.attacks_by_category:
                        self.attacks_by_category[category] = []
                    self.attacks_by_category[category].append(attack)

            except Exception as e:
                print(f"Error loading {json_file}: {e}")
                continue

        return len(self.attacks)

    def get_all_attacks(self) -> List[Attack]:
        """Get all loaded attacks"""
        return self.attacks

    def get_attack_by_id(self, attack_id: str) -> Optional[Attack]:
        """Get specific attack by ID"""
        return self.attacks_by_id.get(attack_id)

    def get_attacks_by_category(self, category: str) -> List[Attack]:
        """Get all attacks in a category"""
        return self.attacks_by_category.get(category, [])

    def get_attacks_by_severity(self, severity: str) -> List[Attack]:
        """Get all attacks with given severity"""
        return [a for a in self.attacks if a.severity == severity]

    def get_categories(self) -> List[str]:
        """Get list of all categories"""
        return list(self.attacks_by_category.keys())

    def get_statistics(self) -> Dict[str, any]:
        """Get statistics about loaded attacks"""
        stats = {
            'total_attacks': len(self.attacks),
            'categories': {},
            'severity_distribution': {
                'low': 0,
                'medium': 0,
                'high': 0,
                'critical': 0
            }
        }

        # Category counts
        for category, attacks in self.attacks_by_category.items():
            stats['categories'][category] = len(attacks)

        # Severity distribution
        for attack in self.attacks:
            if attack.severity in stats['severity_distribution']:
                stats['severity_distribution'][attack.severity] += 1

        return stats

    def filter_attacks(
        self,
        categories: Optional[List[str]] = None,
        severities: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[Attack]:
        """
        Filter attacks by various criteria

        Args:
            categories: List of categories to include
            severities: List of severities to include
            limit: Maximum number of attacks to return

        Returns:
            Filtered list of attacks
        """
        filtered = self.attacks

        if categories:
            filtered = [a for a in filtered if a.category in categories]

        if severities:
            filtered = [a for a in filtered if a.severity in severities]

        if limit:
            filtered = filtered[:limit]

        return filtered

    def __len__(self):
        """Return number of loaded attacks"""
        return len(self.attacks)

    def __repr__(self):
        return f"AttackEngine(attacks={len(self.attacks)}, categories={len(self.attacks_by_category)})"