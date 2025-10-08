/**
 * Custody Tracking Routes
 * Fireblocks integration for digital asset custody monitoring
 */

const express = require('express');
const router = express.Router();
const FireblocksClient = require('../integrations/fireblocks');

// Initialize Fireblocks client
let fireblocksClient;
if (process.env.FIREBLOCKS_API_KEY && process.env.FIREBLOCKS_PRIVATE_KEY_PATH) {
  try {
    fireblocksClient = new FireblocksClient(
      process.env.FIREBLOCKS_API_KEY,
      process.env.FIREBLOCKS_PRIVATE_KEY_PATH
    );
  } catch (error) {
    console.error('Failed to initialize Fireblocks client:', error.message);
  }
}

/**
 * Get vault accounts
 * GET /api/custody/vaults
 */
router.get('/vaults', async (req, res, next) => {
  try {
    if (!fireblocksClient) {
      return res.status(503).json({
        error: 'Fireblocks integration not configured'
      });
    }

    const vaults = await fireblocksClient.getVaultAccounts();

    res.json({
      success: true,
      data: {
        vaults: vaults,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    next(error);
  }
});

/**
 * Get vault account details
 * GET /api/custody/vaults/:vaultId
 */
router.get('/vaults/:vaultId', async (req, res, next) => {
  try {
    const { vaultId } = req.params;

    if (!fireblocksClient) {
      return res.status(503).json({
        error: 'Fireblocks integration not configured'
      });
    }

    const vault = await fireblocksClient.getVaultAccount(vaultId);

    res.json({
      success: true,
      data: vault
    });
  } catch (error) {
    next(error);
  }
});

/**
 * Get custody balances
 * GET /api/custody/balances/:vaultId
 */
router.get('/balances/:vaultId', async (req, res, next) => {
  try {
    const { vaultId } = req.params;

    if (!fireblocksClient) {
      return res.status(503).json({
        error: 'Fireblocks integration not configured'
      });
    }

    const balances = await fireblocksClient.getCustodyBalances(vaultId);

    res.json({
      success: true,
      data: balances
    });
  } catch (error) {
    next(error);
  }
});

/**
 * Get transaction history
 * GET /api/custody/transactions
 */
router.get('/transactions', async (req, res, next) => {
  try {
    if (!fireblocksClient) {
      return res.status(503).json({
        error: 'Fireblocks integration not configured'
      });
    }

    const { after, before, status } = req.query;
    const filters = {};

    if (after) filters.after = parseInt(after);
    if (before) filters.before = parseInt(before);
    if (status) filters.status = status;

    const transactions = await fireblocksClient.getTransactions(filters);

    res.json({
      success: true,
      data: {
        transactions: transactions,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    next(error);
  }
});

/**
 * Generate compliance report
 * POST /api/custody/reports/compliance
 */
router.post('/reports/compliance', async (req, res, next) => {
  try {
    const { vaultId, startDate, endDate } = req.body;

    if (!vaultId || !startDate || !endDate) {
      return res.status(400).json({
        error: 'Vault ID, start date, and end date are required'
      });
    }

    if (!fireblocksClient) {
      return res.status(503).json({
        error: 'Fireblocks integration not configured'
      });
    }

    const report = await fireblocksClient.generateComplianceReport(
      vaultId,
      new Date(startDate),
      new Date(endDate)
    );

    res.json({
      success: true,
      data: report
    });
  } catch (error) {
    next(error);
  }
});

/**
 * Create withdrawal with compliance checks
 * POST /api/custody/withdraw
 */
router.post('/withdraw', async (req, res, next) => {
  try {
    const { sourceVaultId, destinationAddress, asset, amount, note } = req.body;

    if (!sourceVaultId || !destinationAddress || !asset || !amount) {
      return res.status(400).json({
        error: 'All withdrawal details are required'
      });
    }

    if (!fireblocksClient) {
      return res.status(503).json({
        error: 'Fireblocks integration not configured'
      });
    }

    const withdrawal = await fireblocksClient.createWithdrawal({
      sourceVaultId,
      destinationAddress,
      asset,
      amount,
      note
    });

    res.json({
      success: true,
      data: withdrawal
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
