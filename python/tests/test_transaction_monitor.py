"""
Tests for Transaction Monitor
"""
import pytest
from datetime import datetime, timedelta
from aml.transaction_monitor import (
    TransactionMonitor, Transaction, TransactionType, AlertType
)


def test_transaction_monitor_initialization():
    """Test TransactionMonitor initialization"""
    monitor = TransactionMonitor()
    assert monitor.alerts == []
    assert monitor.transaction_history == {}


def test_large_transaction_alert():
    """Test alert generation for large transaction"""
    monitor = TransactionMonitor()
    
    transaction = Transaction(
        transaction_id='tx_001',
        user_id='user_001',
        amount=15000.00,
        currency='USD',
        transaction_type=TransactionType.WITHDRAWAL,
        timestamp=datetime.utcnow()
    )
    
    alerts = monitor.monitor_transaction(transaction)
    
    assert len(alerts) > 0
    assert any(alert.alert_type == AlertType.LARGE_TRANSACTION for alert in alerts)


def test_structuring_detection():
    """Test structuring detection"""
    monitor = TransactionMonitor()
    
    # Create multiple transactions just below CTR threshold
    base_time = datetime.utcnow()
    
    for i in range(4):
        transaction = Transaction(
            transaction_id=f'tx_{i}',
            user_id='user_001',
            amount=9500.00,
            currency='USD',
            transaction_type=TransactionType.WITHDRAWAL,
            timestamp=base_time + timedelta(hours=i)
        )
        alerts = monitor.monitor_transaction(transaction)
    
    # Check if structuring alert was generated
    all_alerts = monitor.get_alerts_by_user('user_001')
    structuring_alerts = [a for a in all_alerts if a.alert_type == AlertType.STRUCTURING]
    
    assert len(structuring_alerts) > 0


def test_velocity_alert():
    """Test velocity alert generation"""
    monitor = TransactionMonitor()
    
    base_time = datetime.utcnow()
    
    # Create many transactions
    for i in range(60):
        transaction = Transaction(
            transaction_id=f'tx_{i}',
            user_id='user_001',
            amount=100.00,
            currency='USD',
            transaction_type=TransactionType.TRANSFER,
            timestamp=base_time + timedelta(minutes=i)
        )
        monitor.monitor_transaction(transaction)
    
    # Check for velocity alert
    all_alerts = monitor.get_alerts_by_user('user_001')
    velocity_alerts = [a for a in all_alerts if a.alert_type == AlertType.VELOCITY]
    
    assert len(velocity_alerts) > 0


def test_get_alerts_by_severity():
    """Test filtering alerts by severity"""
    monitor = TransactionMonitor()
    
    transaction = Transaction(
        transaction_id='tx_001',
        user_id='user_001',
        amount=15000.00,
        currency='USD',
        transaction_type=TransactionType.WITHDRAWAL,
        timestamp=datetime.utcnow()
    )
    
    monitor.monitor_transaction(transaction)
    
    high_severity_alerts = monitor.get_alerts_by_severity('high')
    assert len(high_severity_alerts) > 0
