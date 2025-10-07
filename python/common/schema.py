"""
Database schema definitions for compliance data
"""

CREATE_TABLES_SQL = """
-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(255) PRIMARY KEY,
    customer_type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    nationality VARCHAR(100),
    residence_country VARCHAR(100),
    occupation VARCHAR(255),
    source_of_funds TEXT,
    pep_status BOOLEAN DEFAULT FALSE,
    adverse_media BOOLEAN DEFAULT FALSE,
    risk_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_review_date TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- KYC Documents table
CREATE TABLE IF NOT EXISTS kyc_documents (
    document_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(255) REFERENCES customers(customer_id),
    document_type VARCHAR(100) NOT NULL,
    document_number VARCHAR(255) NOT NULL,
    issue_date DATE NOT NULL,
    expiry_date DATE,
    issuing_authority VARCHAR(255),
    verified BOOLEAN DEFAULT FALSE,
    verification_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Risk Assessments table
CREATE TABLE IF NOT EXISTS risk_assessments (
    assessment_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(255) REFERENCES customers(customer_id),
    risk_level VARCHAR(50) NOT NULL,
    risk_score INTEGER NOT NULL,
    risk_factors TEXT[],
    due_diligence_level VARCHAR(10) NOT NULL,
    assessment_date TIMESTAMP NOT NULL,
    next_review_date TIMESTAMP NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    amount DECIMAL(20, 8) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    counterparty VARCHAR(255),
    jurisdiction VARCHAR(100),
    blockchain_address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AML Alerts table
CREATE TABLE IF NOT EXISTS aml_alerts (
    alert_id VARCHAR(255) PRIMARY KEY,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    transaction_ids TEXT[],
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(255)
);

-- OFAC Sanctions List table
CREATE TABLE IF NOT EXISTS ofac_sanctions (
    entity_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    program VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    aliases TEXT[],
    identification_numbers TEXT[],
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Blockchain Address Screening table
CREATE TABLE IF NOT EXISTS blockchain_screenings (
    screening_id SERIAL PRIMARY KEY,
    address VARCHAR(255) NOT NULL,
    asset VARCHAR(10) NOT NULL,
    risk_level VARCHAR(50),
    category VARCHAR(100),
    sanctions BOOLEAN DEFAULT FALSE,
    screening_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Custody Accounts table
CREATE TABLE IF NOT EXISTS custody_accounts (
    vault_id VARCHAR(255) PRIMARY KEY,
    customer_id VARCHAR(255) REFERENCES customers(customer_id),
    vault_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_customers_risk_level ON customers(risk_level);
CREATE INDEX IF NOT EXISTS idx_customers_country ON customers(residence_country);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_aml_alerts_user_id ON aml_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_aml_alerts_severity ON aml_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_aml_alerts_status ON aml_alerts(status);
CREATE INDEX IF NOT EXISTS idx_blockchain_screenings_address ON blockchain_screenings(address);
"""

DROP_TABLES_SQL = """
DROP TABLE IF EXISTS blockchain_screenings CASCADE;
DROP TABLE IF EXISTS custody_accounts CASCADE;
DROP TABLE IF EXISTS ofac_sanctions CASCADE;
DROP TABLE IF EXISTS aml_alerts CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS risk_assessments CASCADE;
DROP TABLE IF EXISTS kyc_documents CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
"""
