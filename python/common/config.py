"""
Configuration management for compliance services
"""
import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class ComplianceConfig:
    """Compliance service configuration"""
    
    # OFAC Configuration
    ofac_update_interval_hours: int = 24
    
    # Transaction Monitoring Thresholds
    ctr_threshold: float = 10000.0
    structuring_window_hours: int = 24
    max_transactions_per_day: int = 50
    max_volume_per_day: float = 100000.0
    
    # Database Configuration
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "cryptobeam_compliance"
    db_user: str = "postgres"
    db_password: Optional[str] = None
    
    # API Keys
    chainalysis_api_key: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'ComplianceConfig':
        """Load configuration from environment variables"""
        return cls(
            ofac_update_interval_hours=int(os.getenv('OFAC_UPDATE_INTERVAL_HOURS', '24')),
            ctr_threshold=float(os.getenv('CTR_THRESHOLD', '10000')),
            structuring_window_hours=int(os.getenv('STRUCTURING_WINDOW_HOURS', '24')),
            max_transactions_per_day=int(os.getenv('MAX_TRANSACTIONS_PER_DAY', '50')),
            max_volume_per_day=float(os.getenv('MAX_VOLUME_PER_DAY', '100000')),
            db_host=os.getenv('DB_HOST', 'localhost'),
            db_port=int(os.getenv('DB_PORT', '5432')),
            db_name=os.getenv('DB_NAME', 'cryptobeam_compliance'),
            db_user=os.getenv('DB_USER', 'postgres'),
            db_password=os.getenv('DB_PASSWORD'),
            chainalysis_api_key=os.getenv('CHAINALYSIS_API_KEY'),
        )
