from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID


@dataclass
class Character:
    """Character model representing an agent with all its attributes"""
    name: str
    description: str
    user_id: int
    uuid: UUID
    ticker: str
    image_hash: str
    solana_address: Optional[str] = None
    base_address: str = ""
    created_at: datetime = None
    
    # Fields from personality JSON
    llm_settings: Optional[Dict[str, Any]] = None
    available_tools: Optional[List[str]] = None
    
    # Fields from description in personality JSON
    agent_name: Optional[str] = None
    appearance: Optional[str] = None
    age: Optional[str] = None
    biography: Optional[str] = None
    moral_alignment: Optional[str] = None
    actions: Optional[Dict[str, List[str]]] = None
    beliefs_and_knowledge: Optional[Dict[str, List[str]]] = None
    personality_adjectives: Optional[List[str]] = None
    writing_style: Optional[Dict[str, Any]] = None 