"""
KYC Risk Assessment and CDD/EDD Policy Engine
Implements Customer Due Diligence (CDD) and Enhanced Due Diligence (EDD) workflows
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class RiskLevel(Enum):
    """Customer risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PROHIBITED = "prohibited"


class CustomerType(Enum):
    """Types of customers"""
    INDIVIDUAL = "individual"
    BUSINESS = "business"
    TRUST = "trust"
    NONPROFIT = "nonprofit"


class DocumentType(Enum):
    """KYC document types"""
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    NATIONAL_ID = "national_id"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    BUSINESS_LICENSE = "business_license"
    ARTICLES_OF_INCORPORATION = "articles_of_incorporation"


@dataclass
class KYCDocument:
    """KYC verification document"""
    document_type: DocumentType
    document_number: str
    issue_date: datetime
    expiry_date: Optional[datetime]
    issuing_authority: str
    verified: bool = False
    verification_date: Optional[datetime] = None


@dataclass
class Customer:
    """Customer profile"""
    customer_id: str
    customer_type: CustomerType
    name: str
    date_of_birth: Optional[datetime] = None
    nationality: Optional[str] = None
    residence_country: str = None
    occupation: Optional[str] = None
    source_of_funds: Optional[str] = None
    documents: List[KYCDocument] = field(default_factory=list)
    pep_status: bool = False  # Politically Exposed Person
    adverse_media: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_review_date: Optional[datetime] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM


@dataclass
class RiskAssessment:
    """Risk assessment result"""
    customer_id: str
    risk_level: RiskLevel
    risk_score: int  # 0-100
    risk_factors: List[str]
    due_diligence_level: str  # CDD or EDD
    assessment_date: datetime
    next_review_date: datetime
    notes: str


class KYCRiskEngine:
    """
    KYC Risk Assessment Engine
    Implements CDD/EDD policies based on risk factors
    """
    
    # High-risk countries (FATF list and similar)
    HIGH_RISK_COUNTRIES = {
        'IRAN', 'NORTH KOREA', 'SYRIA', 'MYANMAR', 'AFGHANISTAN',
        'SOMALIA', 'YEMEN', 'LIBYA', 'IRAQ'
    }
    
    # High-risk occupations
    HIGH_RISK_OCCUPATIONS = {
        'MONEY_SERVICES_BUSINESS', 'CASINO', 'GAMBLING', 'PRECIOUS_METALS',
        'ARMS_DEALER', 'CASH_INTENSIVE_BUSINESS'
    }
    
    def __init__(self):
        self.customers: Dict[str, Customer] = {}
        self.assessments: Dict[str, RiskAssessment] = {}
    
    def assess_customer_risk(self, customer: Customer) -> RiskAssessment:
        """
        Perform comprehensive risk assessment on a customer
        
        Args:
            customer: Customer to assess
            
        Returns:
            RiskAssessment with risk level and required due diligence
        """
        risk_score = 0
        risk_factors = []
        
        # Base risk score
        risk_score = 20  # Baseline
        
        # Geographic risk
        if customer.residence_country and customer.residence_country.upper() in self.HIGH_RISK_COUNTRIES:
            risk_score += 25
            risk_factors.append(f"High-risk country: {customer.residence_country}")
        
        # PEP status
        if customer.pep_status:
            risk_score += 30
            risk_factors.append("Politically Exposed Person (PEP)")
        
        # Adverse media
        if customer.adverse_media:
            risk_score += 20
            risk_factors.append("Adverse media coverage")
        
        # Occupation risk
        if customer.occupation and customer.occupation.upper() in self.HIGH_RISK_OCCUPATIONS:
            risk_score += 15
            risk_factors.append(f"High-risk occupation: {customer.occupation}")
        
        # Document verification status
        verified_docs = sum(1 for doc in customer.documents if doc.verified)
        if verified_docs == 0:
            risk_score += 25
            risk_factors.append("No verified documents")
        elif verified_docs < 2:
            risk_score += 10
            risk_factors.append("Insufficient document verification")
        
        # Source of funds
        if not customer.source_of_funds:
            risk_score += 15
            risk_factors.append("Source of funds not declared")
        
        # Customer type risk
        if customer.customer_type in [CustomerType.BUSINESS, CustomerType.TRUST]:
            risk_score += 10
            risk_factors.append("Non-individual customer type")
        
        # Determine risk level
        risk_level = self._calculate_risk_level(risk_score)
        
        # Determine due diligence level
        dd_level = "EDD" if risk_level in [RiskLevel.HIGH, RiskLevel.PROHIBITED] else "CDD"
        
        # Calculate next review date based on risk
        review_periods = {
            RiskLevel.LOW: 365,  # Annual
            RiskLevel.MEDIUM: 180,  # Semi-annual
            RiskLevel.HIGH: 90,  # Quarterly
            RiskLevel.PROHIBITED: 30  # Monthly monitoring
        }
        
        next_review = datetime.utcnow() + timedelta(days=review_periods[risk_level])
        
        assessment = RiskAssessment(
            customer_id=customer.customer_id,
            risk_level=risk_level,
            risk_score=min(risk_score, 100),
            risk_factors=risk_factors,
            due_diligence_level=dd_level,
            assessment_date=datetime.utcnow(),
            next_review_date=next_review,
            notes=f"Risk assessment completed. {dd_level} required."
        )
        
        self.assessments[customer.customer_id] = assessment
        customer.risk_level = risk_level
        customer.last_review_date = datetime.utcnow()
        
        return assessment
    
    def _calculate_risk_level(self, risk_score: int) -> RiskLevel:
        """Calculate risk level from risk score"""
        if risk_score >= 80:
            return RiskLevel.PROHIBITED
        elif risk_score >= 60:
            return RiskLevel.HIGH
        elif risk_score >= 35:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def perform_cdd(self, customer: Customer) -> Dict:
        """
        Perform Customer Due Diligence (CDD)
        Standard verification for low to medium risk customers
        
        Returns:
            Dictionary with CDD requirements and status
        """
        requirements = {
            'identity_verification': False,
            'address_verification': False,
            'source_of_funds': False,
            'beneficial_ownership': False  # For businesses
        }
        
        # Check identity documents
        id_docs = [doc for doc in customer.documents if doc.document_type in [
            DocumentType.PASSPORT, DocumentType.DRIVERS_LICENSE, DocumentType.NATIONAL_ID
        ]]
        requirements['identity_verification'] = any(doc.verified for doc in id_docs)
        
        # Check address documents
        address_docs = [doc for doc in customer.documents if doc.document_type in [
            DocumentType.UTILITY_BILL, DocumentType.BANK_STATEMENT
        ]]
        requirements['address_verification'] = any(doc.verified for doc in address_docs)
        
        # Check source of funds
        requirements['source_of_funds'] = customer.source_of_funds is not None
        
        # Beneficial ownership for businesses
        if customer.customer_type in [CustomerType.BUSINESS, CustomerType.TRUST]:
            # In production, check beneficial ownership records
            requirements['beneficial_ownership'] = False
        else:
            requirements['beneficial_ownership'] = True  # N/A for individuals
        
        cdd_complete = all(requirements.values())
        
        return {
            'cdd_complete': cdd_complete,
            'requirements': requirements,
            'missing_items': [k for k, v in requirements.items() if not v]
        }
    
    def perform_edd(self, customer: Customer) -> Dict:
        """
        Perform Enhanced Due Diligence (EDD)
        Enhanced verification for high-risk customers
        
        Returns:
            Dictionary with EDD requirements and status
        """
        # Start with CDD requirements
        cdd_result = self.perform_cdd(customer)
        
        # Additional EDD requirements
        edd_requirements = {
            'enhanced_identity_verification': False,
            'source_of_wealth': False,
            'business_activities': False,
            'transaction_monitoring': True,  # Always enabled for EDD
            'senior_management_approval': False,
            'adverse_media_check': False,
            'sanctions_screening': False
        }
        
        # Enhanced identity - multiple documents required
        verified_docs = sum(1 for doc in customer.documents if doc.verified)
        edd_requirements['enhanced_identity_verification'] = verified_docs >= 2
        
        # Source of wealth (more detailed than source of funds)
        edd_requirements['source_of_wealth'] = customer.source_of_funds is not None
        
        # Adverse media check
        edd_requirements['adverse_media_check'] = True  # Assumed performed
        
        # In production, these would be verified through workflows
        edd_requirements['business_activities'] = customer.occupation is not None
        edd_requirements['senior_management_approval'] = False  # Requires manual approval
        edd_requirements['sanctions_screening'] = True  # Assumed performed
        
        all_requirements = {**cdd_result['requirements'], **edd_requirements}
        edd_complete = all(all_requirements.values())
        
        return {
            'edd_complete': edd_complete,
            'cdd_requirements': cdd_result['requirements'],
            'edd_requirements': edd_requirements,
            'missing_items': [k for k, v in all_requirements.items() if not v]
        }
    
    def get_customers_for_review(self) -> List[Customer]:
        """Get customers that need periodic review"""
        customers_needing_review = []
        
        for customer in self.customers.values():
            if customer.customer_id in self.assessments:
                assessment = self.assessments[customer.customer_id]
                if datetime.utcnow() >= assessment.next_review_date:
                    customers_needing_review.append(customer)
        
        return customers_needing_review
