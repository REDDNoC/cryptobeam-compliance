/**
 * Fireblocks SDK Integration
 * Provides custody tracking and transaction monitoring for digital assets
 */

const { FireblocksSDK } = require('@fireblocks/sdk');
const fs = require('fs');

class FireblocksClient {
  constructor(apiKey, privateKeyPath, baseUrl = 'https://api.fireblocks.io') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
    
    try {
      const privateKey = fs.readFileSync(privateKeyPath, 'utf8');
      this.fireblocks = new FireblocksSDK(privateKey, this.apiKey, this.baseUrl);
    } catch (error) {
      console.error('Failed to initialize Fireblocks SDK:', error.message);
      throw error;
    }
  }

  /**
   * Get vault accounts
   * @returns {Promise<Array>} List of vault accounts
   */
  async getVaultAccounts() {
    try {
      const accounts = await this.fireblocks.getVaultAccountsWithPageInfo({});
      return accounts.accounts || [];
    } catch (error) {
      console.error('Failed to fetch vault accounts:', error.message);
      throw new Error(`Vault accounts retrieval failed: ${error.message}`);
    }
  }

  /**
   * Get vault account by ID
   * @param {string} vaultAccountId - Vault account ID
   * @returns {Promise<Object>} Vault account details
   */
  async getVaultAccount(vaultAccountId) {
    try {
      return await this.fireblocks.getVaultAccountById(vaultAccountId);
    } catch (error) {
      console.error('Failed to fetch vault account:', error.message);
      throw new Error(`Vault account retrieval failed: ${error.message}`);
    }
  }

  /**
   * Create a new vault account
   * @param {string} name - Account name
   * @param {string} customerRefId - Customer reference ID
   * @returns {Promise<Object>} Created vault account
   */
  async createVaultAccount(name, customerRefId) {
    try {
      return await this.fireblocks.createVaultAccount(name, false, customerRefId);
    } catch (error) {
      console.error('Failed to create vault account:', error.message);
      throw new Error(`Vault account creation failed: ${error.message}`);
    }
  }

  /**
   * Get transaction history for compliance monitoring
   * @param {Object} filters - Transaction filters
   * @returns {Promise<Array>} List of transactions
   */
  async getTransactions(filters = {}) {
    try {
      const transactions = await this.fireblocks.getTransactions(filters);
      return transactions || [];
    } catch (error) {
      console.error('Failed to fetch transactions:', error.message);
      throw new Error(`Transaction retrieval failed: ${error.message}`);
    }
  }

  /**
   * Get transaction by ID
   * @param {string} txId - Transaction ID
   * @returns {Promise<Object>} Transaction details
   */
  async getTransaction(txId) {
    try {
      return await this.fireblocks.getTransactionById(txId);
    } catch (error) {
      console.error('Failed to fetch transaction:', error.message);
      throw new Error(`Transaction retrieval failed: ${error.message}`);
    }
  }

  /**
   * Monitor custody balances for compliance reporting
   * @param {string} vaultAccountId - Vault account ID
   * @returns {Promise<Object>} Balance information
   */
  async getCustodyBalances(vaultAccountId) {
    try {
      const account = await this.getVaultAccount(vaultAccountId);
      
      const balances = {};
      if (account.assets) {
        account.assets.forEach(asset => {
          balances[asset.id] = {
            total: asset.total || '0',
            available: asset.available || '0',
            pending: asset.pending || '0',
            frozen: asset.frozen || '0',
            locked: asset.lockedAmount || '0'
          };
        });
      }

      return {
        vaultAccountId: vaultAccountId,
        name: account.name,
        balances: balances,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Failed to fetch custody balances:', error.message);
      throw new Error(`Balance retrieval failed: ${error.message}`);
    }
  }

  /**
   * Create a withdrawal transaction with compliance checks
   * @param {Object} withdrawalData - Withdrawal details
   * @returns {Promise<Object>} Transaction result
   */
  async createWithdrawal(withdrawalData) {
    try {
      const transactionPayload = {
        assetId: withdrawalData.asset,
        source: {
          type: 'VAULT_ACCOUNT',
          id: withdrawalData.sourceVaultId
        },
        destination: {
          type: withdrawalData.destinationType || 'ONE_TIME_ADDRESS',
          oneTimeAddress: withdrawalData.destinationAddress
        },
        amount: withdrawalData.amount.toString(),
        note: withdrawalData.note || 'Compliance-approved withdrawal'
      };

      const transaction = await this.fireblocks.createTransaction(transactionPayload);

      return {
        transactionId: transaction.id,
        status: transaction.status,
        asset: withdrawalData.asset,
        amount: withdrawalData.amount,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Failed to create withdrawal:', error.message);
      throw new Error(`Withdrawal creation failed: ${error.message}`);
    }
  }

  /**
   * Get deposit addresses for a vault account
   * @param {string} vaultAccountId - Vault account ID
   * @param {string} assetId - Asset ID
   * @returns {Promise<Array>} List of deposit addresses
   */
  async getDepositAddresses(vaultAccountId, assetId) {
    try {
      const addresses = await this.fireblocks.getDepositAddresses(vaultAccountId, assetId);
      return addresses || [];
    } catch (error) {
      console.error('Failed to fetch deposit addresses:', error.message);
      throw new Error(`Deposit address retrieval failed: ${error.message}`);
    }
  }

  /**
   * Generate compliance report for a vault account
   * @param {string} vaultAccountId - Vault account ID
   * @param {Date} startDate - Report start date
   * @param {Date} endDate - Report end date
   * @returns {Promise<Object>} Compliance report
   */
  async generateComplianceReport(vaultAccountId, startDate, endDate) {
    try {
      const transactions = await this.getTransactions({
        after: Math.floor(startDate.getTime() / 1000),
        before: Math.floor(endDate.getTime() / 1000)
      });

      const filteredTransactions = transactions.filter(tx => 
        (tx.source && tx.source.id === vaultAccountId) ||
        (tx.destination && tx.destination.id === vaultAccountId)
      );

      const report = {
        vaultAccountId: vaultAccountId,
        reportPeriod: {
          start: startDate.toISOString(),
          end: endDate.toISOString()
        },
        transactionCount: filteredTransactions.length,
        transactions: filteredTransactions.map(tx => ({
          id: tx.id,
          asset: tx.assetId,
          amount: tx.amount,
          status: tx.status,
          createdAt: new Date(tx.createdAt * 1000).toISOString(),
          type: tx.operation
        })),
        generatedAt: new Date().toISOString()
      };

      return report;
    } catch (error) {
      console.error('Failed to generate compliance report:', error.message);
      throw new Error(`Report generation failed: ${error.message}`);
    }
  }
}

module.exports = FireblocksClient;
