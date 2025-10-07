# Example Usage Guide

This guide provides practical examples of using the Cryptobeam Compliance Framework.

## Python Examples

### Example 1: OFAC Sanctions Screening

```python
from sanctions.ofac_screener import OFACScreener, SanctionedEntity

# Initialize the screener
screener = OFACScreener()

# Load sanctions list (in production, this would come from OFAC API/feed)
sanctions_data = [
    {
        'name': 'Sanctioned Person',
        'entity_type': 'individual',
        'program': 'SDN',
        'country': 'IRAN',
        'aliases': ['S. Person', 'SP'],
        'identification_numbers': ['ID12345']
    }
]

screener.load_sanctions_list(sanctions_data)

# Screen a customer
result = screener.screen_individual('John Doe', country='US')

if result.is_match:
    print(f"⚠️  SANCTIONS MATCH DETECTED")
    print(f"Risk Level: {result.risk_level}")
    print(f"Matched Entities: {len(result.matched_entities)}")
    for entity in result.matched_entities:
        print(f"  - {entity.name} ({entity.program})")
else:
    print("✅ No sanctions matches found")
```

### Example 2: Transaction Monitoring

```python
from aml.transaction_monitor import TransactionMonitor, Transaction, TransactionType
from datetime import datetime

# Initialize monitor
monitor = TransactionMonitor()

# Create a transaction
transaction = Transaction(
    transaction_id='tx_001',
    user_id='user_123',
    amount=15000.00,
    currency='USD',
    transaction_type=TransactionType.WITHDRAWAL,
    timestamp=datetime.utcnow(),
    counterparty='Bank Account',
    jurisdiction='US'
)

# Monitor the transaction
alerts = monitor.monitor_transaction(transaction)

# Handle alerts
for alert in alerts:
    print(f"🚨 Alert: {alert.alert_type.value}")
    print(f"   Severity: {alert.severity}")
    print(f"   Description: {alert.description}")
    
    if alert.severity == 'critical':
        # Take immediate action
        print("   ⚠️  CRITICAL - Requires immediate review")
    elif alert.severity == 'high':
        # Schedule review
        print("   📋 HIGH - Schedule review within 24 hours")
```

### Example 3: KYC Risk Assessment

```python
from kyc.risk_assessment import (
    KYCRiskEngine, Customer, CustomerType, 
    KYCDocument, DocumentType
)
from datetime import datetime

# Initialize engine
engine = KYCRiskEngine()

# Create customer
customer = Customer(
    customer_id='cust_001',
    customer_type=CustomerType.INDIVIDUAL,
    name='Alice Johnson',
    residence_country='US',
    occupation='Software Engineer',
    source_of_funds='Employment Salary',
    pep_status=False,
    adverse_media=False
)

# Add KYC documents
customer.documents.append(KYCDocument(
    document_type=DocumentType.PASSPORT,
    document_number='P123456789',
    issue_date=datetime(2020, 1, 1),
    expiry_date=datetime(2030, 1, 1),
    issuing_authority='US Department of State',
    verified=True,
    verification_date=datetime.utcnow()
))

customer.documents.append(KYCDocument(
    document_type=DocumentType.UTILITY_BILL,
    document_number='UTIL-2024-001',
    issue_date=datetime(2024, 1, 1),
    expiry_date=None,
    issuing_authority='Electric Company',
    verified=True,
    verification_date=datetime.utcnow()
))

# Assess risk
assessment = engine.assess_customer_risk(customer)

print(f"Customer: {customer.name}")
print(f"Risk Level: {assessment.risk_level.value}")
print(f"Risk Score: {assessment.risk_score}/100")
print(f"Due Diligence Required: {assessment.due_diligence_level}")
print(f"Next Review Date: {assessment.next_review_date.strftime('%Y-%m-%d')}")

if assessment.risk_factors:
    print("\nRisk Factors:")
    for factor in assessment.risk_factors:
        print(f"  - {factor}")

# Perform appropriate due diligence
if assessment.due_diligence_level == 'CDD':
    cdd_result = engine.perform_cdd(customer)
    print(f"\nCDD Complete: {cdd_result['cdd_complete']}")
    if not cdd_result['cdd_complete']:
        print("Missing items:")
        for item in cdd_result['missing_items']:
            print(f"  - {item}")
else:
    edd_result = engine.perform_edd(customer)
    print(f"\nEDD Complete: {edd_result['edd_complete']}")
    if not edd_result['edd_complete']:
        print("Missing items:")
        for item in edd_result['missing_items']:
            print(f"  - {item}")
```

## Node.js API Examples

### Example 1: Screen Cryptocurrency Address

```bash
curl -X POST http://localhost:3000/api/sanctions/screen-address \
  -H "Content-Type: application/json" \
  -d '{
    "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    "asset": "BTC"
  }' | jq
```

### Example 2: Assess Withdrawal Risk

```bash
curl -X POST http://localhost:3000/api/sanctions/assess-withdrawal \
  -H "Content-Type: application/json" \
  -d '{
    "destinationAddress": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    "asset": "BTC",
    "amount": 5.0
  }' | jq
```

### Example 3: Monitor Transaction

```bash
curl -X POST http://localhost:3000/api/aml/monitor-transaction \
  -H "Content-Type: application/json" \
  -d '{
    "transactionId": "tx_12345",
    "userId": "user_001",
    "amount": 25000,
    "currency": "USD",
    "type": "deposit"
  }' | jq
```

### Example 4: Assess Customer Risk

```bash
curl -X POST http://localhost:3000/api/kyc/assess-risk \
  -H "Content-Type: application/json" \
  -d '{
    "customerId": "cust_001",
    "name": "John Smith",
    "country": "US",
    "occupation": "Teacher",
    "pepStatus": false,
    "adverseMedia": false
  }' | jq
```

### Example 5: Get Vault Balances

```bash
curl http://localhost:3000/api/custody/balances/vault_123 | jq
```

### Example 6: Generate Compliance Report

```bash
curl -X POST http://localhost:3000/api/custody/reports/compliance \
  -H "Content-Type: application/json" \
  -d '{
    "vaultId": "vault_123",
    "startDate": "2024-01-01",
    "endDate": "2024-12-31"
  }' | jq
```

## Integration Examples

### Example: Complete Customer Onboarding Flow

```python
from kyc.risk_assessment import KYCRiskEngine, Customer, CustomerType
from sanctions.ofac_screener import OFACScreener

# Step 1: Create customer record
customer = Customer(
    customer_id='new_customer_001',
    customer_type=CustomerType.INDIVIDUAL,
    name='Jane Doe',
    residence_country='US'
)

# Step 2: Screen against sanctions
screener = OFACScreener()
screener.load_sanctions_list(sanctions_data)
sanctions_result = screener.screen_individual(customer.name, customer.residence_country)

if sanctions_result.is_match:
    print("❌ Customer failed sanctions screening - APPLICATION REJECTED")
    exit()

# Step 3: Assess risk
engine = KYCRiskEngine()
assessment = engine.assess_customer_risk(customer)

# Step 4: Determine next steps
if assessment.risk_level.value == 'prohibited':
    print("❌ Risk level: PROHIBITED - APPLICATION REJECTED")
elif assessment.due_diligence_level == 'EDD':
    print("⚠️  Enhanced Due Diligence Required")
    print("Required documents:")
    print("  - Government ID (verified)")
    print("  - Proof of address")
    print("  - Source of wealth documentation")
    print("  - Senior management approval")
else:
    print("✅ Standard Due Diligence Required")
    print("Required documents:")
    print("  - Government ID")
    print("  - Proof of address")
    print("  - Source of funds declaration")
```

### Example: Real-time Transaction Screening

```python
from aml.transaction_monitor import TransactionMonitor, Transaction, TransactionType
from datetime import datetime
import requests  # For Chainalysis integration

def process_crypto_withdrawal(user_id, amount, asset, destination_address):
    """Process cryptocurrency withdrawal with compliance checks"""
    
    # Step 1: Screen destination address (via API)
    response = requests.post('http://localhost:3000/api/sanctions/screen-address', 
        json={
            'address': destination_address,
            'asset': asset
        }
    )
    
    screening = response.json()['data']
    
    if screening.get('sanctions'):
        return {
            'approved': False,
            'reason': 'Destination address is sanctioned'
        }
    
    # Step 2: Assess withdrawal risk
    response = requests.post('http://localhost:3000/api/sanctions/assess-withdrawal',
        json={
            'destinationAddress': destination_address,
            'asset': asset,
            'amount': amount
        }
    )
    
    risk_assessment = response.json()['data']
    
    if risk_assessment['recommendation'] == 'BLOCK':
        return {
            'approved': False,
            'reason': f"High risk: {', '.join(risk_assessment['riskFactors'])}"
        }
    
    # Step 3: Monitor transaction
    monitor = TransactionMonitor()
    transaction = Transaction(
        transaction_id=f'tx_{datetime.utcnow().timestamp()}',
        user_id=user_id,
        amount=amount,
        currency=asset,
        transaction_type=TransactionType.CRYPTO_TRANSFER,
        timestamp=datetime.utcnow(),
        blockchain_address=destination_address
    )
    
    alerts = monitor.monitor_transaction(transaction)
    
    # Check for critical alerts
    critical_alerts = [a for a in alerts if a.severity == 'critical']
    if critical_alerts:
        return {
            'approved': False,
            'reason': 'Transaction triggered critical AML alerts',
            'alerts': [a.description for a in critical_alerts]
        }
    
    # Approved (possibly with conditions)
    return {
        'approved': True,
        'transaction_id': transaction.transaction_id,
        'alerts': [a.description for a in alerts] if alerts else []
    }

# Usage
result = process_crypto_withdrawal(
    user_id='user_123',
    amount=2.5,
    asset='BTC',
    destination_address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
)

if result['approved']:
    print("✅ Withdrawal approved")
    if result.get('alerts'):
        print("ℹ️  Alerts generated:")
        for alert in result['alerts']:
            print(f"  - {alert}")
else:
    print(f"❌ Withdrawal rejected: {result['reason']}")
```

## Testing Examples

### Running Python Tests

```bash
# Run all tests
cd python
pytest tests/ -v

# Run specific test file
pytest tests/test_ofac_screener.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Testing the API

```bash
# Start the API server
cd nodejs
npm start

# In another terminal, run health check
curl http://localhost:3000/health

# Test endpoints
curl -X POST http://localhost:3000/api/kyc/assess-risk \
  -H "Content-Type: application/json" \
  -d '{
    "customerId": "test_001",
    "name": "Test User",
    "country": "US",
    "pepStatus": false,
    "adverseMedia": false
  }'
```

## Production Considerations

1. **API Keys**: Store in secure vault (AWS Secrets Manager, HashiCorp Vault)
2. **Rate Limiting**: Implement on all API endpoints
3. **Authentication**: Add JWT or API key authentication
4. **Logging**: Implement comprehensive audit logging
5. **Monitoring**: Set up alerts for critical compliance events
6. **Database**: Use connection pooling and proper indexing
7. **Caching**: Cache sanctions lists with regular updates
8. **Backup**: Regular backups of compliance data
9. **Encryption**: Encrypt sensitive data at rest and in transit
10. **Compliance**: Regular audits and regulatory updates
