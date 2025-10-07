/**
 * AML Monitoring Routes
 * Transaction monitoring and alert management endpoints
 */

const express = require('express');
const router = express.Router();
const ChainalysisClient = require('../integrations/chainalysis');

// Initialize Chainalysis client
let chainalysisClient;
if (process.env.CHAINALYSIS_API_KEY) {
  chainalysisClient = new ChainalysisClient(process.env.CHAINALYSIS_API_KEY);
}

/**
 * Monitor a transaction
 * POST /api/aml/monitor-transaction
 */
router.post('/monitor-transaction', async (req, res, next) => {
  try {
    const { transactionId, userId, amount, currency, type } = req.body;

    if (!transactionId || !userId || !amount) {
      return res.status(400).json({
        error: 'Transaction ID, user ID, and amount are required'
      });
    }

    // In production, this would process through transaction monitoring engine
    const alerts = [];

    // Check for large transactions (CTR threshold)
    if (amount >= 10000) {
      alerts.push({
        alertType: 'LARGE_TRANSACTION',
        severity: 'high',
        description: `Large transaction of ${amount} ${currency || 'USD'} exceeds CTR threshold`,
        transactionId: transactionId
      });
    }

    res.json({
      success: true,
      data: {
        transactionId: transactionId,
        monitored: true,
        alerts: alerts,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    next(error);
  }
});

/**
 * Register a blockchain transfer for monitoring
 * POST /api/aml/register-transfer
 */
router.post('/register-transfer', async (req, res, next) => {
  try {
    const { transferReference, asset, amount, direction, address } = req.body;

    if (!transferReference || !asset || !amount || !direction || !address) {
      return res.status(400).json({
        error: 'All transfer details are required'
      });
    }

    if (!chainalysisClient) {
      return res.status(503).json({
        error: 'Chainalysis integration not configured'
      });
    }

    const result = await chainalysisClient.registerTransfer({
      transferReference,
      asset,
      amount,
      direction,
      address
    });

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    next(error);
  }
});

/**
 * Get alerts for a user
 * GET /api/aml/alerts/:userId
 */
router.get('/alerts/:userId', async (req, res, next) => {
  try {
    const { userId } = req.params;

    if (!chainalysisClient) {
      // Return mock alerts if Chainalysis not configured
      return res.json({
        success: true,
        data: {
          userId: userId,
          alerts: [],
          timestamp: new Date().toISOString()
        }
      });
    }

    const alerts = await chainalysisClient.getUserAlerts(userId);

    res.json({
      success: true,
      data: {
        userId: userId,
        alerts: alerts,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    next(error);
  }
});

/**
 * Monitor blockchain transaction
 * POST /api/aml/monitor-blockchain-tx
 */
router.post('/monitor-blockchain-tx', async (req, res, next) => {
  try {
    const { txHash, asset } = req.body;

    if (!txHash || !asset) {
      return res.status(400).json({
        error: 'Transaction hash and asset are required'
      });
    }

    if (!chainalysisClient) {
      return res.status(503).json({
        error: 'Chainalysis integration not configured'
      });
    }

    const result = await chainalysisClient.monitorTransaction(txHash, asset);

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
