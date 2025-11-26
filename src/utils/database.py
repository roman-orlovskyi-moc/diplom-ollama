"""
Database utilities for storing test results
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from src.models.test_result import TestResult
from config.settings import DATABASE_PATH


class Database:
    """SQLite database for storing test results"""

    def __init__(self, db_path: Path = None):
        self.db_path = db_path or DATABASE_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.connect()

    def connect(self):
        """Connect to database"""
        # Use check_same_thread=False to allow multi-threaded access in Flask
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()

        # Test results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attack_id TEXT NOT NULL,
                attack_name TEXT NOT NULL,
                attack_category TEXT NOT NULL,
                attack_severity TEXT NOT NULL,
                defense_name TEXT NOT NULL,
                attack_successful BOOLEAN NOT NULL,
                response TEXT NOT NULL,
                latency_ms INTEGER NOT NULL,
                tokens_used INTEGER NOT NULL,
                cost REAL NOT NULL,
                model TEXT NOT NULL,
                timestamp REAL NOT NULL,
                metadata TEXT
            )
        """)

        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_attack_id ON test_results(attack_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_defense_name ON test_results(defense_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_attack_category ON test_results(attack_category)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON test_results(timestamp)
        """)

        self.conn.commit()

    def save_result(self, result: TestResult) -> int:
        """
        Save test result to database

        Args:
            result: TestResult instance

        Returns:
            Row ID of inserted record
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO test_results (
                attack_id, attack_name, attack_category, attack_severity,
                defense_name, attack_successful, response, latency_ms,
                tokens_used, cost, model, timestamp, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.attack_id,
            result.attack_name,
            result.attack_category,
            result.attack_severity,
            result.defense_name,
            result.attack_successful,
            result.response,
            result.latency_ms,
            result.tokens_used,
            result.cost,
            result.model,
            result.timestamp,
            json.dumps(result.metadata)
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_all_results(self) -> List[TestResult]:
        """Get all test results"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM test_results ORDER BY timestamp DESC")

        results = []
        for row in cursor.fetchall():
            results.append(self._row_to_result(row))

        return results

    def get_results_by_category(self, category: str) -> List[TestResult]:
        """Get all results for a specific attack category"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM test_results WHERE attack_category = ? ORDER BY timestamp DESC",
            (category,)
        )

        results = []
        for row in cursor.fetchall():
            results.append(self._row_to_result(row))

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics from database"""
        cursor = self.conn.cursor()

        # Total tests
        cursor.execute("SELECT COUNT(*) as count FROM test_results")
        total_tests = cursor.fetchone()['count']

        # Successful attacks
        cursor.execute("SELECT COUNT(*) as count FROM test_results WHERE attack_successful = 1")
        successful_attacks = cursor.fetchone()['count']

        # By defense
        cursor.execute("""
            SELECT defense_name,
                   COUNT(*) as total,
                   SUM(attack_successful) as successful
            FROM test_results
            GROUP BY defense_name
        """)
        by_defense = {}
        for row in cursor.fetchall():
            by_defense[row['defense_name']] = {
                'total': row['total'],
                'successful': row['successful'],
                'success_rate': row['successful'] / row['total'] if row['total'] > 0 else 0
            }

        # By category
        cursor.execute("""
            SELECT attack_category,
                   COUNT(*) as total,
                   SUM(attack_successful) as successful
            FROM test_results
            GROUP BY attack_category
        """)
        by_category = {}
        for row in cursor.fetchall():
            by_category[row['attack_category']] = {
                'total': row['total'],
                'successful': row['successful'],
                'success_rate': row['successful'] / row['total'] if row['total'] > 0 else 0
            }

        return {
            'total_tests': total_tests,
            'successful_attacks': successful_attacks,
            'by_defense': by_defense,
            'by_category': by_category
        }

    def export_to_csv(self, output_path: Path):
        """
        Export results to CSV file

        Args:
            output_path: Path to output CSV file
        """
        import csv

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM test_results ORDER BY timestamp DESC")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Header
            writer.writerow([
                'attack_id', 'attack_name', 'attack_category', 'attack_severity',
                'defense_name', 'attack_successful', 'latency_ms', 'tokens_used',
                'cost', 'model', 'timestamp'
            ])

            # Data
            for row in cursor.fetchall():
                writer.writerow([
                    row['attack_id'],
                    row['attack_name'],
                    row['attack_category'],
                    row['attack_severity'],
                    row['defense_name'],
                    row['attack_successful'],
                    row['latency_ms'],
                    row['tokens_used'],
                    row['cost'],
                    row['model'],
                    row['timestamp']
                ])

    def clear_all(self):
        """Clear all test results"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM test_results")
        self.conn.commit()

    def _row_to_result(self, row) -> TestResult:
        """Convert database row to TestResult"""
        metadata = json.loads(row['metadata']) if row['metadata'] else {}

        return TestResult(
            attack_id=row['attack_id'],
            attack_name=row['attack_name'],
            attack_category=row['attack_category'],
            attack_severity=row['attack_severity'],
            defense_name=row['defense_name'],
            attack_successful=bool(row['attack_successful']),
            response=row['response'],
            latency_ms=row['latency_ms'],
            tokens_used=row['tokens_used'],
            cost=row['cost'],
            model=row['model'],
            timestamp=row['timestamp'],
            metadata=metadata
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()