/**
 * Chainalysis API Integration
 * Provides blockchain transaction monitoring and risk assessment
 */

const axios = require('axios');

class ChainalysisClient {
  constructor(apiKey, baseUrl = 'https://api.chainalysis.com') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: this.baseUrl,
      headers: {
        'Token': this.apiKey,
        'Content-Type': 'application/json'
      }
    });
  }

  /**
   * Screen a cryptocurrency address for sanctions and risk
   * @param {string} address - Cryptocurrency address
   * @param {string} asset - Asset type (BTC, ETH, etc.)
   * @returns {Promise<Object>} Screening result
   */
  async screenAddress(address, asset = 'BTC') {
    try {
      const response = await this.client.post('/api/risk/v2/entities', {
        address: address,
        asset: asset
      });

      return {
        address: address,
        asset: asset,
        riskLevel: response.data.risk || 'unknown',
        cluster: response.data.cluster,
        category: response.data.category,
        categoryId: response.data.categoryId,
        sanctions: response.data.sanctions || false,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Chainalysis screening error:', error.message);
      throw new Error(`Failed to screen address: ${error.message}`);
    }
  }

  /**
   * Monitor a transaction for suspicious activity
   * @param {string} txHash - Transaction hash
   * @param {string} asset - Asset type
   * @returns {Promise<Object>} Transaction analysis
   */
  async monitorTransaction(txHash, asset = 'BTC') {
    try {
      const response = await this.client.get(`/api/kyt/v2/users/${asset}/transfers/${txHash}`);

      return {
        txHash: txHash,
        asset: asset,
        riskScore: response.data.riskScore || 0,
        alerts: response.data.alerts || [],
        exposure: response.data.exposure || {},
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Transaction monitoring error:', error.message);
      throw new Error(`Failed to monitor transaction: ${error.message}`);
    }
  }

  /**
   * Register a transfer for monitoring
   * @param {Object} transferData - Transfer details
   * @returns {Promise<Object>} Registration result
   */
  async registerTransfer(transferData) {
    try {
      const response = await this.client.post('/api/kyt/v2/users/transfers', {
        network: transferData.asset,
        asset: transferData.asset,
        transferReference: transferData.transferReference,
        direction: transferData.direction, // 'sent' or 'received'
        assetAmount: transferData.amount,
        address: transferData.address,
        outputAddress: transferData.outputAddress
      });

      return {
        transferReference: transferData.transferReference,
        registered: true,
        externalId: response.data.externalId,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Transfer registration error:', error.message);
      throw new Error(`Failed to register transfer: ${error.message}`);
    }
  }

  /**
   * Get alerts for a specific user
   * @param {string} userId - User identifier
   * @returns {Promise<Array>} List of alerts
   */
  async getUserAlerts(userId) {
    try {
      const response = await this.client.get(`/api/kyt/v2/users/${userId}/alerts`);
      
      return response.data.alerts || [];
    } catch (error) {
      console.error('Failed to fetch alerts:', error.message);
      return [];
    }
  }

  /**
   * Assess withdrawal risk
   * @param {Object} withdrawalData - Withdrawal details
   * @returns {Promise<Object>} Risk assessment
   */
  async assessWithdrawalRisk(withdrawalData) {
    try {
      const addressScreening = await this.screenAddress(
        withdrawalData.destinationAddress,
        withdrawalData.asset
      );

      // Calculate risk score based on Chainalysis data
      let riskScore = 0;
      let riskFactors = [];

      if (addressScreening.sanctions) {
        riskScore += 100;
        riskFactors.push('Address is sanctioned');
      }

      if (addressScreening.riskLevel === 'severe') {
        riskScore += 75;
        riskFactors.push('Severe risk level');
      } else if (addressScreening.riskLevel === 'high') {
        riskScore += 50;
        riskFactors.push('High risk level');
      } else if (addressScreening.riskLevel === 'medium') {
        riskScore += 25;
        riskFactors.push('Medium risk level');
      }

      // Check category
      const highRiskCategories = ['darknet', 'mixer', 'scam', 'ransomware', 'stolen funds'];
      if (addressScreening.category && highRiskCategories.includes(addressScreening.category.toLowerCase())) {
        riskScore += 60;
        riskFactors.push(`High-risk category: ${addressScreening.category}`);
      }

      return {
        approved: riskScore < 50,
        riskScore: Math.min(riskScore, 100),
        riskFactors: riskFactors,
        addressScreening: addressScreening,
        recommendation: riskScore >= 75 ? 'BLOCK' : riskScore >= 50 ? 'REVIEW' : 'APPROVE',
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Withdrawal risk assessment error:', error.message);
      throw new Error(`Failed to assess withdrawal: ${error.message}`);
    }
  }
}

module.exports = ChainalysisClient;
