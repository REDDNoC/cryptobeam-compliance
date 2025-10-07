"""
Tests for OFAC Screener
"""
import pytest
from datetime import datetime
from sanctions.ofac_screener import OFACScreener, SanctionedEntity


def test_ofac_screener_initialization():
    """Test OFACScreener initialization"""
    screener = OFACScreener()
    assert screener.sanctions_list == []
    assert screener.last_update is None


def test_load_sanctions_list():
    """Test loading sanctions list"""
    screener = OFACScreener()
    
    sanctions_data = [
        {
            'name': 'John Terrorist',
            'entity_type': 'individual',
            'program': 'SDN',
            'country': 'IRAN',
            'aliases': ['J. Terror', 'Johnny T'],
            'identification_numbers': ['ID12345']
        }
    ]
    
    screener.load_sanctions_list(sanctions_data)
    
    assert len(screener.sanctions_list) == 1
    assert screener.sanctions_list[0].name == 'John Terrorist'
    assert screener.last_update is not None


def test_screen_individual_exact_match():
    """Test screening individual with exact match"""
    screener = OFACScreener()
    
    sanctions_data = [
        {
            'name': 'John Terrorist',
            'entity_type': 'individual',
            'program': 'SDN',
            'country': 'IRAN'
        }
    ]
    
    screener.load_sanctions_list(sanctions_data)
    result = screener.screen_individual('John Terrorist')
    
    assert result.is_match is True
    assert result.risk_level == 'high'
    assert len(result.matched_entities) == 1


def test_screen_individual_no_match():
    """Test screening individual with no match"""
    screener = OFACScreener()
    
    sanctions_data = [
        {
            'name': 'John Terrorist',
            'entity_type': 'individual',
            'program': 'SDN',
            'country': 'IRAN'
        }
    ]
    
    screener.load_sanctions_list(sanctions_data)
    result = screener.screen_individual('Jane Doe')
    
    assert result.is_match is False
    assert result.risk_level == 'low'
    assert len(result.matched_entities) == 0


def test_screen_entity():
    """Test screening organization"""
    screener = OFACScreener()
    
    sanctions_data = [
        {
            'name': 'Evil Corporation',
            'entity_type': 'organization',
            'program': 'SDN',
            'country': 'NORTH KOREA'
        }
    ]
    
    screener.load_sanctions_list(sanctions_data)
    result = screener.screen_entity('Evil Corporation', 'organization', 'NORTH KOREA')
    
    assert result.is_match is True
    assert result.risk_level == 'high'


def test_normalize_name():
    """Test name normalization"""
    screener = OFACScreener()
    
    assert screener._normalize_name('John Doe') == 'john doe'
    assert screener._normalize_name('  John  Doe  ') == 'john  doe'
    assert screener._normalize_name('John D.') == 'john d'
