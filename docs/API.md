# API Documentation

## Base URL
```
http://localhost:3000/api
```

## Authentication
Currently, the API does not require authentication. In production, implement proper authentication (e.g., API keys, JWT tokens).

## Endpoints

### Health Check

#### GET /health
Check API server health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "Cryptobeam Compliance API"
}
```

---

### Sanctions Screening

#### POST /api/sanctions/screen-address
Screen a cryptocurrency address against sanctions lists.

**Request Body:**
```json
{
  "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
  "asset": "BTC"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    "asset": "BTC",
    "riskLevel": "low",
    "cluster": "...",
    "category": "exchange",
    "sanctions": false,
    "timestamp": "2024-01-15T10:30:00.000Z"
  }
}
```

#### POST /api/sanctions/screen-name
Screen an individual or entity name against OFAC lists.

**Request Body:**
```json
{
  "name": "John Doe",
  "type": "individual",
  "country": "US"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "John Doe",
    "type": "individual",
    "country": "US",
    "isMatch": false,
    "riskLevel": "low",
    "matchedEntities": [],
    "screeningTimestamp": "2024-01-15T10:30:00.000Z"
  }
}
```

#### POST /api/sanctions/assess-withdrawal
Assess risk for a cryptocurrency withdrawal.

**Request Body:**
```json
{
  "destinationAddress": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
  "asset": "BTC",
  "amount": 1.5
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "approved": true,
    "riskScore": 15,
    "riskFactors": [],
    "addressScreening": {...},
    "recommendation": "APPROVE",
    "timestamp": "2024-01-15T10:30:00.000Z"
  }
}
```

---

### AML Monitoring

#### POST /api/aml/monitor-transaction
Monitor a transaction for AML compliance.

**Request Body:**
```json
{
  "transactionId": "tx_12345",
  "userId": "user_001",
  "amount": 15000,
  "currency": "USD",
  "type": "withdrawal"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transactionId": "tx_12345",
    "monitored": true,
    "alerts": [
      {
        "alertType": "LARGE_TRANSACTION",
        "severity": "high",
        "description": "Large transaction of 15000 USD exceeds CTR threshold",
        "transactionId": "tx_12345"
      }
    ],
    "timestamp": "2024-01-15T10:30:00.000Z"
  }
}
```

#### POST /api/aml/register-transfer
Register a blockchain transfer for monitoring.

**Request Body:**
```json
{
  "transferReference": "transfer_001",
  "asset": "BTC",
  "amount": 1.5,
  "direction": "sent",
  "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
}
```

#### GET /api/aml/alerts/:userId
Get all AML alerts for a user.

**Response:**
```json
{
  "success": true,
  "data": {
    "userId": "user_001",
    "alerts": [...],
    "timestamp": "2024-01-15T10:30:00.000Z"
  }
}
```

---

### KYC

#### POST /api/kyc/assess-risk
Assess customer risk level.

**Request Body:**
```json
{
  "customerId": "cust_001",
  "customerType": "individual",
  "name": "Jane Smith",
  "country": "US",
  "occupation": "Engineer",
  "pepStatus": false,
  "adverseMedia": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "customerId": "cust_001",
    "riskLevel": "low",
    "riskScore": 20,
    "riskFactors": [],
    "dueDiligenceLevel": "CDD",
    "assessmentDate": "2024-01-15T10:30:00.000Z"
  }
}
```

---

### Custody

#### GET /api/custody/vaults
Get all vault accounts.

#### GET /api/custody/balances/:vaultId
Get custody balances for a vault.

**Response:**
```json
{
  "success": true,
  "data": {
    "vaultAccountId": "vault_123",
    "name": "Customer Vault",
    "balances": {
      "BTC": {
        "total": "10.5",
        "available": "10.0",
        "pending": "0.5",
        "frozen": "0",
        "locked": "0"
      }
    },
    "timestamp": "2024-01-15T10:30:00.000Z"
  }
}
```

---

## Error Responses

All endpoints return errors in the following format:

```json
{
  "error": {
    "message": "Error description",
    "status": 400
  }
}
```

### Common Error Codes
- `400`: Bad Request - Invalid parameters
- `404`: Not Found - Endpoint does not exist
- `500`: Internal Server Error
- `503`: Service Unavailable - External integration not configured
