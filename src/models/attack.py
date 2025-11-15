"""
Attack pattern data model
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional


@dataclass
class SuccessCriteria:
    """Criteria for determining if an attack succeeded"""
    type: str  # contains_forbidden_content, role_broken, data_leaked
    patterns: Optional[List[str]] = None
    forbidden_topics: Optional[List[str]] = None
    sensitive_patterns: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SuccessCriteria':
        return cls(
            type=data['type'],
            patterns=data.get('patterns'),
            forbidden_topics=data.get('forbidden_topics'),
            sensitive_patterns=data.get('sensitive_patterns')
        )


@dataclass
class AttackContext:
    """Context for executing an attack"""
    system_prompt: str
    user_message: str
    document_content: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttackContext':
        return cls(
            system_prompt=data['system_prompt'],
            user_message=data['user_message'],
            document_content=data.get('document_content')
        )


@dataclass
class Attack:
    """Represents a single prompt injection attack pattern"""
    id: str
    name: str
    description: str
    severity: str  # low, medium, high, critical
    category: str
    context: AttackContext
    expected_behavior: str
    attack_indicators: List[str]
    success_criteria: SuccessCriteria

    @classmethod
    def from_dict(cls, data: Dict[str, Any], category: str) -> 'Attack':
        """Create Attack instance from dictionary"""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            severity=data['severity'],
            category=category,
            context=AttackContext.from_dict(data['context']),
            expected_behavior=data['expected_behavior'],
            attack_indicators=data['attack_indicators'],
            success_criteria=SuccessCriteria.from_dict(data['success_criteria'])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'severity': self.severity,
            'category': self.category,
            'context': {
                'system_prompt': self.context.system_prompt,
                'user_message': self.context.user_message,
                'document_content': self.context.document_content
            },
            'expected_behavior': self.expected_behavior,
            'attack_indicators': self.attack_indicators,
            'success_criteria': {
                'type': self.success_criteria.type,
                'patterns': self.success_criteria.patterns,
                'forbidden_topics': self.success_criteria.forbidden_topics,
                'sensitive_patterns': self.success_criteria.sensitive_patterns
            }
        }