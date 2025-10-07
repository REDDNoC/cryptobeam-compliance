"""
Tests for KYC Risk Assessment
"""
import pytest
from datetime import datetime
from kyc.risk_assessment import (
    KYCRiskEngine, Customer, CustomerType, RiskLevel, 
    KYCDocument, DocumentType
)


def test_kyc_risk_engine_initialization():
    """Test KYCRiskEngine initialization"""
    engine = KYCRiskEngine()
    assert engine.customers == {}
    assert engine.assessments == {}


def test_assess_low_risk_customer():
    """Test risk assessment for low-risk customer"""
    engine = KYCRiskEngine()
    
    customer = Customer(
        customer_id='cust_001',
        customer_type=CustomerType.INDIVIDUAL,
        name='John Doe',
        residence_country='US',
        occupation='Engineer',
        source_of_funds='Employment',
        pep_status=False,
        adverse_media=False
    )
    
    # Add verified documents
    customer.documents.append(KYCDocument(
        document_type=DocumentType.PASSPORT,
        document_number='P123456',
        issue_date=datetime(2020, 1, 1),
        expiry_date=datetime(2030, 1, 1),
        issuing_authority='US Government',
        verified=True,
        verification_date=datetime.utcnow()
    ))
    
    assessment = engine.assess_customer_risk(customer)
    
    assert assessment.risk_level == RiskLevel.LOW
    assert assessment.due_diligence_level == 'CDD'


def test_assess_high_risk_customer():
    """Test risk assessment for high-risk customer"""
    engine = KYCRiskEngine()
    
    customer = Customer(
        customer_id='cust_002',
        customer_type=CustomerType.INDIVIDUAL,
        name='Jane Smith',
        residence_country='IRAN',  # High-risk country
        pep_status=True,  # Politically exposed person
        adverse_media=True
    )
    
    assessment = engine.assess_customer_risk(customer)
    
    assert assessment.risk_level in [RiskLevel.HIGH, RiskLevel.PROHIBITED]
    assert assessment.due_diligence_level == 'EDD'
    assert len(assessment.risk_factors) > 0


def test_perform_cdd():
    """Test CDD requirements check"""
    engine = KYCRiskEngine()
    
    customer = Customer(
        customer_id='cust_003',
        customer_type=CustomerType.INDIVIDUAL,
        name='Bob Johnson',
        source_of_funds='Salary'
    )
    
    # Add verified documents
    customer.documents.append(KYCDocument(
        document_type=DocumentType.PASSPORT,
        document_number='P789012',
        issue_date=datetime(2020, 1, 1),
        expiry_date=datetime(2030, 1, 1),
        issuing_authority='US Government',
        verified=True
    ))
    
    customer.documents.append(KYCDocument(
        document_type=DocumentType.UTILITY_BILL,
        document_number='UB123',
        issue_date=datetime(2024, 1, 1),
        expiry_date=None,
        issuing_authority='Utility Company',
        verified=True
    ))
    
    cdd_result = engine.perform_cdd(customer)
    
    assert cdd_result['cdd_complete'] is True
    assert cdd_result['requirements']['identity_verification'] is True
    assert cdd_result['requirements']['address_verification'] is True


def test_perform_edd():
    """Test EDD requirements check"""
    engine = KYCRiskEngine()
    
    customer = Customer(
        customer_id='cust_004',
        customer_type=CustomerType.INDIVIDUAL,
        name='Alice Williams',
        source_of_funds='Business',
        occupation='CEO',
        pep_status=True
    )
    
    # Add multiple verified documents for EDD
    customer.documents.append(KYCDocument(
        document_type=DocumentType.PASSPORT,
        document_number='P345678',
        issue_date=datetime(2020, 1, 1),
        expiry_date=datetime(2030, 1, 1),
        issuing_authority='Government',
        verified=True
    ))
    
    customer.documents.append(KYCDocument(
        document_type=DocumentType.UTILITY_BILL,
        document_number='UB456',
        issue_date=datetime(2024, 1, 1),
        expiry_date=None,
        issuing_authority='Utility',
        verified=True
    ))
    
    edd_result = engine.perform_edd(customer)
    
    assert 'edd_requirements' in edd_result
    assert edd_result['edd_requirements']['transaction_monitoring'] is True
