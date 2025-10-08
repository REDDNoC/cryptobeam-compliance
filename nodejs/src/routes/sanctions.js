/**
 * Sanctions Screening Routes
 * OFAC and sanctions list screening endpoints
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
 * Screen a cryptocurrency address
 * POST /api/sanctions/screen-address
 */
router.post('/screen-address', async (req, res, next) => {
  try {
    const { address, asset } = req.body;

    if (!address) {
      return res.status(400).json({
        error: 'Address is required'
      });
    }

    if (!chainalysisClient) {
      return res.status(503).json({
        error: 'Chainalysis integration not configured'
      });
    }

    const result = await chainalysisClient.screenAddress(address, asset || 'BTC');

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    next(error);
  }
});

/**
 * Screen an individual or entity name
 * POST /api/sanctions/screen-name
 */
router.post('/screen-name', async (req, res, next) => {
  try {
    const { name, type, country } = req.body;

    if (!name) {
      return res.status(400).json({
        error: 'Name is required'
      });
    }

    // In production, this would call OFAC screening service
    // For now, return a mock response
    res.json({
      success: true,
      data: {
        name: name,
        type: type || 'individual',
        country: country,
        isMatch: false,
        riskLevel: 'low',
        matchedEntities: [],
        screeningTimestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    next(error);
  }
});

/**
 * Assess withdrawal risk
 * POST /api/sanctions/assess-withdrawal
 */
router.post('/assess-withdrawal', async (req, res, next) => {
  try {
    const { destinationAddress, asset, amount } = req.body;

    if (!destinationAddress || !asset) {
      return res.status(400).json({
        error: 'Destination address and asset are required'
      });
    }

    if (!chainalysisClient) {
      return res.status(503).json({
        error: 'Chainalysis integration not configured'
      });
    }

    const assessment = await chainalysisClient.assessWithdrawalRisk({
      destinationAddress,
      asset,
      amount
    });

    res.json({
      success: true,
      data: assessment
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
