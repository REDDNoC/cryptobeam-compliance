/**
 * KYC Routes
 * Customer verification and risk assessment endpoints
 */

const express = require('express');
const router = express.Router();
const PlaidClient = require('../integrations/plaid');

// Initialize Plaid client
let plaidClient;
if (process.env.PLAID_CLIENT_ID && process.env.PLAID_SECRET) {
  plaidClient = new PlaidClient(
    process.env.PLAID_CLIENT_ID,
    process.env.PLAID_SECRET,
    process.env.PLAID_ENV || 'sandbox'
  );
}

/**
 * Create Plaid Link token
 * POST /api/kyc/create-link-token
 */
router.post('/create-link-token', async (req, res, next) => {
  try {
    const { userId, clientName } = req.body;

    if (!userId) {
      return res.status(400).json({
        error: 'User ID is required'
      });
    }

    if (!plaidClient) {
      return res.status(503).json({
        error: 'Plaid integration not configured'
      });
    }

    const result = await plaidClient.createLinkToken(userId, clientName);

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    next(error);
  }
});

/**
 * Exchange public token for access token
 * POST /api/kyc/exchange-token
 */
router.post('/exchange-token', async (req, res, next) => {
  try {
    const { publicToken } = req.body;

    if (!publicToken) {
      return res.status(400).json({
        error: 'Public token is required'
      });
    }

    if (!plaidClient) {
      return res.status(503).json({
        error: 'Plaid integration not configured'
      });
    }

    const result = await plaidClient.exchangePublicToken(publicToken);

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    next(error);
  }
});

/**
 * Verify identity
 * POST /api/kyc/verify-identity
 */
router.post('/verify-identity', async (req, res, next) => {
  try {
    const { accessToken } = req.body;

    if (!accessToken) {
      return res.status(400).json({
        error: 'Access token is required'
      });
    }

    if (!plaidClient) {
      return res.status(503).json({
        error: 'Plaid integration not configured'
      });
    }

    const result = await plaidClient.getIdentity(accessToken);

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    next(error);
  }
});

/**
 * Verify source of funds
 * POST /api/kyc/verify-source-of-funds
 */
router.post('/verify-source-of-funds', async (req, res, next) => {
  try {
    const { accessToken } = req.body;

    if (!accessToken) {
      return res.status(400).json({
        error: 'Access token is required'
      });
    }

    if (!plaidClient) {
      return res.status(503).json({
        error: 'Plaid integration not configured'
      });
    }

    const result = await plaidClient.verifySourceOfFunds(accessToken);

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    next(error);
  }
});

/**
 * Assess customer risk
 * POST /api/kyc/assess-risk
 */
router.post('/assess-risk', async (req, res, next) => {
  try {
    const {
      customerId,
      customerType,
      name,
      country,
      occupation,
      pepStatus,
      adverseMedia
    } = req.body;

    if (!customerId || !name) {
      return res.status(400).json({
        error: 'Customer ID and name are required'
      });
    }

    // Calculate risk score based on provided factors
    let riskScore = 20; // Baseline
    const riskFactors = [];

    // High-risk countries
    const highRiskCountries = ['IRAN', 'NORTH KOREA', 'SYRIA', 'MYANMAR'];
    if (country && highRiskCountries.includes(country.toUpperCase())) {
      riskScore += 25;
      riskFactors.push(`High-risk country: ${country}`);
    }

    // PEP status
    if (pepStatus) {
      riskScore += 30;
      riskFactors.push('Politically Exposed Person (PEP)');
    }

    // Adverse media
    if (adverseMedia) {
      riskScore += 20;
      riskFactors.push('Adverse media coverage');
    }

    // Determine risk level
    let riskLevel;
    let dueDiligenceLevel;

    if (riskScore >= 80) {
      riskLevel = 'prohibited';
      dueDiligenceLevel = 'EDD';
    } else if (riskScore >= 60) {
      riskLevel = 'high';
      dueDiligenceLevel = 'EDD';
    } else if (riskScore >= 35) {
      riskLevel = 'medium';
      dueDiligenceLevel = 'CDD';
    } else {
      riskLevel = 'low';
      dueDiligenceLevel = 'CDD';
    }

    res.json({
      success: true,
      data: {
        customerId: customerId,
        riskLevel: riskLevel,
        riskScore: Math.min(riskScore, 100),
        riskFactors: riskFactors,
        dueDiligenceLevel: dueDiligenceLevel,
        assessmentDate: new Date().toISOString()
      }
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
