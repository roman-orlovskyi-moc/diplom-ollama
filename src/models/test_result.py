"""
Test result data model
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any
import time


@dataclass
class TestResult:
    """Represents the result of a single attack test"""
    attack_id: str
    attack_name: str
    attack_category: str
    attack_severity: str
    defense_name: str
    attack_successful: bool
    response: str
    latency_ms: int
    tokens_used: int
    cost: float
    timestamp: float
    metadata: Dict[str, Any]

    @classmethod
    def create(
        cls,
        attack_id: str,
        attack_name: str,
        attack_category: str,
        attack_severity: str,
        defense_name: str,
        attack_successful: bool,
        response: str,
        latency_ms: int,
        tokens_used: int = 0,
        cost: float = 0.0,
        metadata: Dict[str, Any] = None
    ) -> 'TestResult':
        """Create a new test result"""
        return cls(
            attack_id=attack_id,
            attack_name=attack_name,
            attack_category=attack_category,
            attack_severity=attack_severity,
            defense_name=defense_name,
            attack_successful=attack_successful,
            response=response,
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            cost=cost,
            timestamp=time.time(),
            metadata=metadata or {}
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestResult':
        """Create from dictionary"""
        return cls(**data)