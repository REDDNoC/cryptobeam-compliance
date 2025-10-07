# Cryptobeam Compliance Framework

AML / KYC / Sanctions Compliance Framework: Implements AML compliance workflows aligned with BSA, FinCEN, and OFAC standards. Automated monitoring via Chainalysis, CDD/EDD policies, and Fireblocks-integrated custody tracking.

## Overview

This framework provides comprehensive compliance tools for financial institutions and cryptocurrency businesses, implementing industry-standard AML (Anti-Money Laundering), KYC (Know Your Customer), and sanctions screening processes.

### Key Features

- **OFAC Sanctions Screening**: Screen individuals and entities against OFAC sanctions lists
- **Transaction Monitoring**: Automated AML monitoring with BSA/FinCEN compliance
- **Risk Assessment**: CDD/EDD policy engine for customer risk evaluation
- **Blockchain Monitoring**: Chainalysis integration for crypto transaction screening
- **Custody Tracking**: Fireblocks integration for digital asset custody management
- **Banking Verification**: Plaid integration for identity and source of funds verification

## Tech Stack

- **Python 3.8+**: Core compliance engine
- **Node.js 16+**: API services and integrations
- **PostgreSQL**: Data persistence
- **Chainalysis API**: Blockchain analytics and monitoring
- **Plaid API**: Banking data and identity verification
- **Fireblocks SDK**: Digital asset custody and transactions

## Architecture

```
cryptobeam-compliance/
├── python/                 # Python compliance engine
│   ├── aml/               # AML monitoring services
│   ├── kyc/               # KYC and risk assessment
│   ├── sanctions/         # OFAC screening
│   ├── common/            # Shared utilities and config
│   └── tests/             # Python tests
├── nodejs/                # Node.js API services
│   ├── src/
│   │   ├── integrations/  # External API integrations
│   │   ├── routes/        # API endpoints
│   │   └── middleware/    # Express middleware
│   └── tests/             # Node.js tests
└── docs/                  # Documentation
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- PostgreSQL 12 or higher

### Python Setup

```bash
cd python
pip install -r requirements.txt
```

### Node.js Setup

```bash
cd nodejs
npm install
```

### Database Setup

```bash
# Create PostgreSQL database
createdb cryptobeam_compliance

# Initialize schema (using psql)
psql cryptobeam_compliance < python/common/schema.py
```

### Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys and configuration
```

## Configuration

Configure the following environment variables in `.env`:

- `CHAINALYSIS_API_KEY`: Your Chainalysis API key
- `PLAID_CLIENT_ID`: Plaid client ID
- `PLAID_SECRET`: Plaid secret key
- `FIREBLOCKS_API_KEY`: Fireblocks API key
- `FIREBLOCKS_PRIVATE_KEY_PATH`: Path to Fireblocks private key file
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: PostgreSQL configuration

## Usage

### Starting the API Server

```bash
cd nodejs
npm start
```

The API server will start on `http://localhost:3000`.

### Python Compliance Engine

#### OFAC Sanctions Screening

```python
from sanctions.ofac_screener import OFACScreener, SanctionedEntity

# Initialize screener
screener = OFACScreener()

# Load sanctions list (from OFAC data source)
screener.load_sanctions_list(sanctions_data)

# Screen an individual
result = screener.screen_individual("John Doe", country="US")

if result.is_match:
    print(f"Match found! Risk level: {result.risk_level}")
    print(f"Matched entities: {result.matched_entities}")
```

#### Transaction Monitoring

```python
from aml.transaction_monitor import TransactionMonitor, Transaction, TransactionType
from datetime import datetime

# Initialize monitor
monitor = TransactionMonitor()

# Monitor a transaction
transaction = Transaction(
    transaction_id="tx_12345",
    user_id="user_001",
    amount=15000.00,
    currency="USD",
    transaction_type=TransactionType.WITHDRAWAL,
    timestamp=datetime.utcnow()
)

alerts = monitor.monitor_transaction(transaction)

for alert in alerts:
    print(f"Alert: {alert.alert_type} - {alert.description}")
```

#### KYC Risk Assessment

```python
from kyc.risk_assessment import KYCRiskEngine, Customer, CustomerType
from datetime import datetime

# Initialize risk engine
risk_engine = KYCRiskEngine()

# Create customer profile
customer = Customer(
    customer_id="cust_001",
    customer_type=CustomerType.INDIVIDUAL,
    name="Jane Smith",
    residence_country="US",
    occupation="Software Engineer",
    pep_status=False
)

# Assess risk
assessment = risk_engine.assess_customer_risk(customer)
print(f"Risk Level: {assessment.risk_level}")
print(f"Risk Score: {assessment.risk_score}")
print(f"Due Diligence: {assessment.due_diligence_level}")

# Perform CDD
cdd_result = risk_engine.perform_cdd(customer)
print(f"CDD Complete: {cdd_result['cdd_complete']}")
```

### API Endpoints

#### Sanctions Screening

```bash
# Screen a cryptocurrency address
curl -X POST http://localhost:3000/api/sanctions/screen-address \
  -H "Content-Type: application/json" \
  -d '{"address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "asset": "BTC"}'

# Screen a name
curl -X POST http://localhost:3000/api/sanctions/screen-name \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "type": "individual", "country": "US"}'

# Assess withdrawal risk
curl -X POST http://localhost:3000/api/sanctions/assess-withdrawal \
  -H "Content-Type: application/json" \
  -d '{
    "destinationAddress": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    "asset": "BTC",
    "amount": 1.5
  }'
```

#### AML Monitoring

```bash
# Monitor a transaction
curl -X POST http://localhost:3000/api/aml/monitor-transaction \
  -H "Content-Type: application/json" \
  -d '{
    "transactionId": "tx_12345",
    "userId": "user_001",
    "amount": 15000,
    "currency": "USD",
    "type": "withdrawal"
  }'

# Get user alerts
curl http://localhost:3000/api/aml/alerts/user_001
```

#### KYC

```bash
# Assess customer risk
curl -X POST http://localhost:3000/api/kyc/assess-risk \
  -H "Content-Type: application/json" \
  -d '{
    "customerId": "cust_001",
    "name": "Jane Smith",
    "country": "US",
    "pepStatus": false,
    "adverseMedia": false
  }'

# Create Plaid Link token
curl -X POST http://localhost:3000/api/kyc/create-link-token \
  -H "Content-Type: application/json" \
  -d '{"userId": "user_001", "clientName": "My App"}'
```

#### Custody

```bash
# Get vault accounts
curl http://localhost:3000/api/custody/vaults

# Get custody balances
curl http://localhost:3000/api/custody/balances/vault_123

# Generate compliance report
curl -X POST http://localhost:3000/api/custody/reports/compliance \
  -H "Content-Type: application/json" \
  -d '{
    "vaultId": "vault_123",
    "startDate": "2024-01-01",
    "endDate": "2024-12-31"
  }'
```

## Compliance Standards

This framework implements the following regulatory standards:

### BSA (Bank Secrecy Act)
- Currency Transaction Reports (CTR) for transactions ≥ $10,000
- Suspicious Activity Reports (SAR) generation
- Customer Identification Program (CIP)

### FinCEN Requirements
- Transaction monitoring and reporting
- Recordkeeping requirements
- Structuring detection (anti-smurfing)

### OFAC Compliance
- Sanctions list screening
- Blocked persons and entities checking
- Real-time transaction screening

### KYC/AML Best Practices
- Customer Due Diligence (CDD)
- Enhanced Due Diligence (EDD) for high-risk customers
- Ongoing monitoring and periodic reviews
- PEP (Politically Exposed Person) screening
- Adverse media checks

## Testing

### Python Tests

```bash
cd python
pytest tests/
```

### Node.js Tests

```bash
cd nodejs
npm test
```

## Security Considerations

- **API Keys**: Never commit API keys to version control. Use environment variables.
- **Database**: Ensure PostgreSQL is properly secured with strong passwords and network restrictions.
- **Data Encryption**: Sensitive customer data should be encrypted at rest and in transit.
- **Access Control**: Implement proper authentication and authorization for API endpoints.
- **Audit Logging**: All compliance actions should be logged for audit trails.

## Contributing

This is a compliance framework. All changes must be reviewed for regulatory compliance before merging.

## License

MIT License - See LICENSE file for details

## Disclaimer

This framework provides tools for compliance workflows but does not guarantee regulatory compliance. Organizations must:
- Implement proper policies and procedures
- Conduct regular compliance audits
- Maintain qualified compliance staff
- Stay updated with regulatory changes
- Consult with legal and compliance advisors

## Support

For issues and questions, please open a GitHub issue or contact the compliance team.

## References

- [FinCEN Regulations](https://www.fincen.gov/resources/statutes-and-regulations)
- [OFAC Sanctions Programs](https://ofac.treasury.gov/sanctions-programs-and-country-information)
- [FATF Recommendations](https://www.fatf-gafi.org/recommendations.html)
- [Chainalysis API Documentation](https://docs.chainalysis.com/)
- [Plaid API Documentation](https://plaid.com/docs/)
- [Fireblocks API Documentation](https://developers.fireblocks.com/)
