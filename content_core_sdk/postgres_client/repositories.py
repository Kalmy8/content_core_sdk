from typing import Any
from content_core_sdk.postgres_client.client import PostgresService
from content_core_sdk.postgres_client.models import Character
import json


class CharacterRepository:
    """Repository for accessing character data from the database"""
    
    def __init__(self, db_service: PostgresService) -> None:
        self.db = db_service
        
    async def get_character_by_name(self, character_name: str) -> Character | None:
        """
        Retrieve a character by name from the database.
        
        Args:
            character_name: The name of the character to retrieve
            
        Returns:
            Character instance or None if not found
        """
        query = """
        SELECT id, user_id, uuid, name, ticker, description, personality, 
               image_hash, solana_address, base_address, created_at
        FROM agent
        WHERE name = $1
        """
        
        record = await self.db.fetchrow(query, character_name)
        if not record:
            return None
            
        agent_record = dict(record)
        personality_data = json.loads(agent_record['personality'])
        
        # Convert from database record to Character model, including all personality fields
        return Character(
            name=agent_record['name'],
            description=agent_record['description'],
            user_id=agent_record['user_id'],
            uuid=agent_record['uuid'],
            ticker=agent_record['ticker'],
            image_hash=agent_record['image_hash'],
            solana_address=agent_record.get('solana_address'),
            base_address=agent_record['base_address'],
            created_at=agent_record['created_at'],
            llm_settings=personality_data.get('llm_settings'),
            available_tools=personality_data.get('available_tools'),
            agent_name=personality_data.get('description', {}).get('agentName'),
            appearance=personality_data.get('description', {}).get('appearance'),
            age=personality_data.get('description', {}).get('age'),
            origin=personality_data.get('description', {}).get('origin'),
            persona_description=personality_data.get('description', {}).get('persona'),
            moral_alignment=personality_data.get('description', {}).get('moralAlignment'),
            actions=personality_data.get('description', {}).get('actions'),
            beliefs_and_knowledge=personality_data.get('description', {}).get('beliefsAndKnowledge'),
            personality_adjectives=personality_data.get('description', {}).get('personalityAdjectives'),
            writing_style=personality_data.get('description', {}).get('writingStyle')
        ) 