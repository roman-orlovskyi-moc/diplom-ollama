"""
Attack pattern data model
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional


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

    @classmethod
    def from_dict(cls, data: Dict[str, Any], category: str) -> 'Attack':
        """Create Attack instance from dictionary"""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            severity=data['severity'],
            category=category,
            context=AttackContext.from_dict(data['context'])
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
            }
        }