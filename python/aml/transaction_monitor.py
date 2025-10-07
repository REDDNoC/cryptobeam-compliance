"""
Transaction Monitoring Service
Implements automated transaction monitoring for AML compliance
Aligned with BSA and FinCEN requirements
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class TransactionType(Enum):
    """Types of transactions to monitor"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    CRYPTO_PURCHASE = "crypto_purchase"
    CRYPTO_SALE = "crypto_sale"
    CRYPTO_TRANSFER = "crypto_transfer"


class AlertType(Enum):
    """Types of AML alerts"""
    STRUCTURING = "structuring"  # Smurfing/structuring to avoid CTR
    VELOCITY = "velocity"  # High transaction velocity
    LARGE_TRANSACTION = "large_transaction"  # Single large transaction
    UNUSUAL_PATTERN = "unusual_pattern"  # Deviation from baseline
    HIGH_RISK_JURISDICTION = "high_risk_jurisdiction"
    ROUND_AMOUNT = "round_amount"  # Suspicious round amounts


@dataclass
class Transaction:
    """Represents a financial transaction"""
    transaction_id: str
    user_id: str
    amount: float
    currency: str
    transaction_type: TransactionType
    timestamp: datetime
    counterparty: Optional[str] = None
    jurisdiction: Optional[str] = None
    blockchain_address: Optional[str] = None
    
    
@dataclass
class AMLAlert:
    """AML monitoring alert"""
    alert_id: str
    alert_type: AlertType
    severity: str  # critical, high, medium, low
    transaction_ids: List[str]
    user_id: str
    description: str
    created_at: datetime
    metadata: Dict


class TransactionMonitor:
    """
    Transaction Monitoring Service
    Detects suspicious patterns and generates AML alerts
    """
    
    # FinCEN thresholds
    CTR_THRESHOLD = 10000  # Currency Transaction Report threshold
    STRUCTURING_THRESHOLD = 10000  # Detect attempts to avoid CTR
    STRUCTURING_WINDOW_HOURS = 24
    
    # Velocity thresholds
    MAX_TRANSACTIONS_PER_DAY = 50
    MAX_VOLUME_PER_DAY = 100000
    
    def __init__(self):
        self.alerts: List[AMLAlert] = []
        self.transaction_history: Dict[str, List[Transaction]] = {}
    
    def monitor_transaction(self, transaction: Transaction) -> List[AMLAlert]:
        """
        Monitor a transaction and generate alerts if suspicious patterns detected
        
        Args:
            transaction: Transaction to monitor
            
        Returns:
            List of generated alerts
        """
        alerts = []
        
        # Store transaction in history
        if transaction.user_id not in self.transaction_history:
            self.transaction_history[transaction.user_id] = []
        self.transaction_history[transaction.user_id].append(transaction)
        
        # Check for large transactions (CTR threshold)
        if transaction.amount >= self.CTR_THRESHOLD:
            alerts.append(self._create_alert(
                AlertType.LARGE_TRANSACTION,
                'high',
                [transaction.transaction_id],
                transaction.user_id,
                f'Large transaction of {transaction.amount} {transaction.currency} exceeds CTR threshold'
            ))
        
        # Check for structuring
        structuring_alert = self._check_structuring(transaction)
        if structuring_alert:
            alerts.append(structuring_alert)
        
        # Check velocity
        velocity_alert = self._check_velocity(transaction)
        if velocity_alert:
            alerts.append(velocity_alert)
        
        # Check for round amounts (potential indicator of structuring)
        round_amount_alert = self._check_round_amounts(transaction)
        if round_amount_alert:
            alerts.append(round_amount_alert)
        
        # Check high-risk jurisdictions
        jurisdiction_alert = self._check_jurisdiction(transaction)
        if jurisdiction_alert:
            alerts.append(jurisdiction_alert)
        
        self.alerts.extend(alerts)
        return alerts
    
    def _check_structuring(self, transaction: Transaction) -> Optional[AMLAlert]:
        """
        Detect potential structuring (breaking large amounts into smaller transactions)
        """
        user_txns = self.transaction_history.get(transaction.user_id, [])
        
        # Get transactions in the last 24 hours
        cutoff_time = transaction.timestamp - timedelta(hours=self.STRUCTURING_WINDOW_HOURS)
        recent_txns = [
            txn for txn in user_txns
            if txn.timestamp >= cutoff_time and txn.transaction_type == transaction.transaction_type
        ]
        
        if len(recent_txns) < 3:
            return None
        
        # Calculate total amount
        total_amount = sum(txn.amount for txn in recent_txns)
        
        # If total exceeds threshold but individual transactions are below
        if total_amount >= self.STRUCTURING_THRESHOLD:
            all_below_threshold = all(txn.amount < self.CTR_THRESHOLD for txn in recent_txns)
            if all_below_threshold and len(recent_txns) >= 3:
                return self._create_alert(
                    AlertType.STRUCTURING,
                    'critical',
                    [txn.transaction_id for txn in recent_txns],
                    transaction.user_id,
                    f'Potential structuring: {len(recent_txns)} transactions totaling {total_amount} in {self.STRUCTURING_WINDOW_HOURS}h',
                    {'total_amount': total_amount, 'transaction_count': len(recent_txns)}
                )
        
        return None
    
    def _check_velocity(self, transaction: Transaction) -> Optional[AMLAlert]:
        """Check for unusual transaction velocity"""
        user_txns = self.transaction_history.get(transaction.user_id, [])
        
        # Get transactions in the last 24 hours
        cutoff_time = transaction.timestamp - timedelta(hours=24)
        recent_txns = [txn for txn in user_txns if txn.timestamp >= cutoff_time]
        
        # Check count velocity
        if len(recent_txns) > self.MAX_TRANSACTIONS_PER_DAY:
            return self._create_alert(
                AlertType.VELOCITY,
                'high',
                [txn.transaction_id for txn in recent_txns[-10:]],  # Last 10 transactions
                transaction.user_id,
                f'High transaction velocity: {len(recent_txns)} transactions in 24h',
                {'transaction_count': len(recent_txns)}
            )
        
        # Check volume velocity
        total_volume = sum(txn.amount for txn in recent_txns)
        if total_volume > self.MAX_VOLUME_PER_DAY:
            return self._create_alert(
                AlertType.VELOCITY,
                'high',
                [txn.transaction_id for txn in recent_txns[-10:]],
                transaction.user_id,
                f'High transaction volume: {total_volume} in 24h',
                {'total_volume': total_volume}
            )
        
        return None
    
    def _check_round_amounts(self, transaction: Transaction) -> Optional[AMLAlert]:
        """Check for suspicious round amounts"""
        # Check if amount is a round number (e.g., 5000, 9000, 9500)
        if transaction.amount >= 1000:
            if transaction.amount % 1000 == 0 or transaction.amount % 500 == 0:
                # Get recent round amount transactions
                user_txns = self.transaction_history.get(transaction.user_id, [])
                cutoff_time = transaction.timestamp - timedelta(hours=24)
                recent_round_txns = [
                    txn for txn in user_txns
                    if txn.timestamp >= cutoff_time and (txn.amount % 1000 == 0 or txn.amount % 500 == 0)
                ]
                
                if len(recent_round_txns) >= 3:
                    return self._create_alert(
                        AlertType.ROUND_AMOUNT,
                        'medium',
                        [txn.transaction_id for txn in recent_round_txns],
                        transaction.user_id,
                        f'Multiple round amount transactions: {len(recent_round_txns)} in 24h',
                        {'transaction_count': len(recent_round_txns)}
                    )
        
        return None
    
    def _check_jurisdiction(self, transaction: Transaction) -> Optional[AMLAlert]:
        """Check for high-risk jurisdictions"""
        # FATF high-risk jurisdictions (example list)
        high_risk_jurisdictions = {
            'IRAN', 'NORTH KOREA', 'SYRIA', 'MYANMAR'
        }
        
        if transaction.jurisdiction and transaction.jurisdiction.upper() in high_risk_jurisdictions:
            return self._create_alert(
                AlertType.HIGH_RISK_JURISDICTION,
                'critical',
                [transaction.transaction_id],
                transaction.user_id,
                f'Transaction from high-risk jurisdiction: {transaction.jurisdiction}',
                {'jurisdiction': transaction.jurisdiction}
            )
        
        return None
    
    def _create_alert(
        self,
        alert_type: AlertType,
        severity: str,
        transaction_ids: List[str],
        user_id: str,
        description: str,
        metadata: Optional[Dict] = None
    ) -> AMLAlert:
        """Create an AML alert"""
        import uuid
        
        return AMLAlert(
            alert_id=str(uuid.uuid4()),
            alert_type=alert_type,
            severity=severity,
            transaction_ids=transaction_ids,
            user_id=user_id,
            description=description,
            created_at=datetime.utcnow(),
            metadata=metadata or {}
        )
    
    def get_alerts_by_user(self, user_id: str) -> List[AMLAlert]:
        """Get all alerts for a specific user"""
        return [alert for alert in self.alerts if alert.user_id == user_id]
    
    def get_alerts_by_severity(self, severity: str) -> List[AMLAlert]:
        """Get alerts filtered by severity"""
        return [alert for alert in self.alerts if alert.severity == severity]
