"""
OFAC Sanctions Screening Module
Implements sanctions list screening aligned with OFAC standards
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib


@dataclass
class SanctionedEntity:
    """Represents a sanctioned entity from OFAC lists"""
    name: str
    entity_type: str  # individual, organization, vessel, aircraft
    program: str  # SDN, Non-SDN, Sectoral Sanctions
    country: Optional[str] = None
    aliases: List[str] = None
    identification_numbers: List[str] = None
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.identification_numbers is None:
            self.identification_numbers = []


@dataclass
class ScreeningResult:
    """Result of OFAC sanctions screening"""
    is_match: bool
    risk_level: str  # high, medium, low
    matched_entities: List[SanctionedEntity]
    screening_timestamp: datetime
    match_score: float  # 0.0 to 1.0


class OFACScreener:
    """
    OFAC Sanctions Screening Engine
    Screens individuals and entities against OFAC sanctions lists
    """
    
    def __init__(self):
        self.sanctions_list: List[SanctionedEntity] = []
        self.last_update: Optional[datetime] = None
    
    def load_sanctions_list(self, sanctions_data: List[Dict]) -> None:
        """
        Load OFAC sanctions list data
        
        Args:
            sanctions_data: List of dictionaries containing sanctions data
        """
        self.sanctions_list = [
            SanctionedEntity(**entity) for entity in sanctions_data
        ]
        self.last_update = datetime.utcnow()
    
    def screen_individual(self, name: str, country: Optional[str] = None) -> ScreeningResult:
        """
        Screen an individual against OFAC sanctions lists
        
        Args:
            name: Full name of individual
            country: Country of residence/citizenship
            
        Returns:
            ScreeningResult with match details
        """
        matched_entities = []
        max_score = 0.0
        
        normalized_name = self._normalize_name(name)
        
        for entity in self.sanctions_list:
            if entity.entity_type != 'individual':
                continue
            
            # Check exact match
            if self._normalize_name(entity.name) == normalized_name:
                matched_entities.append(entity)
                max_score = max(max_score, 1.0)
                continue
            
            # Check aliases
            for alias in entity.aliases:
                if self._normalize_name(alias) == normalized_name:
                    matched_entities.append(entity)
                    max_score = max(max_score, 0.95)
                    break
            
            # Fuzzy matching
            similarity = self._calculate_similarity(normalized_name, self._normalize_name(entity.name))
            if similarity > 0.85:
                if entity not in matched_entities:
                    matched_entities.append(entity)
                max_score = max(max_score, similarity)
        
        risk_level = self._determine_risk_level(max_score, matched_entities)
        
        return ScreeningResult(
            is_match=len(matched_entities) > 0,
            risk_level=risk_level,
            matched_entities=matched_entities,
            screening_timestamp=datetime.utcnow(),
            match_score=max_score
        )
    
    def screen_entity(self, entity_name: str, entity_type: str, country: Optional[str] = None) -> ScreeningResult:
        """
        Screen an organization/entity against OFAC sanctions lists
        
        Args:
            entity_name: Name of the organization
            entity_type: Type of entity (organization, vessel, aircraft)
            country: Country of registration
            
        Returns:
            ScreeningResult with match details
        """
        matched_entities = []
        max_score = 0.0
        
        normalized_name = self._normalize_name(entity_name)
        
        for entity in self.sanctions_list:
            if entity.entity_type != entity_type:
                continue
            
            # Exact match
            if self._normalize_name(entity.name) == normalized_name:
                matched_entities.append(entity)
                max_score = 1.0
                continue
            
            # Country match increases suspicion
            country_match = country and entity.country and entity.country.lower() == country.lower()
            
            # Fuzzy matching with country boost
            similarity = self._calculate_similarity(normalized_name, self._normalize_name(entity.name))
            if country_match:
                similarity = min(1.0, similarity * 1.1)
            
            if similarity > 0.80:
                if entity not in matched_entities:
                    matched_entities.append(entity)
                max_score = max(max_score, similarity)
        
        risk_level = self._determine_risk_level(max_score, matched_entities)
        
        return ScreeningResult(
            is_match=len(matched_entities) > 0,
            risk_level=risk_level,
            matched_entities=matched_entities,
            screening_timestamp=datetime.utcnow(),
            match_score=max_score
        )
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        return name.lower().strip().replace('.', '').replace(',', '')
    
    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity score between two names using simple approach
        In production, use advanced algorithms like Levenshtein distance
        """
        # Simple token-based similarity
        tokens1 = set(name1.split())
        tokens2 = set(name2.split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union)
    
    def _determine_risk_level(self, score: float, matches: List[SanctionedEntity]) -> str:
        """Determine risk level based on match score and entities"""
        if not matches:
            return 'low'
        
        if score >= 0.95:
            return 'high'
        elif score >= 0.85:
            return 'medium'
        else:
            return 'low'
