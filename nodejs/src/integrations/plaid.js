/**
 * Plaid API Integration
 * Provides banking data access and verification for KYC/AML compliance
 */

const { Configuration, PlaidApi, PlaidEnvironments } = require('plaid');

class PlaidClient {
  constructor(clientId, secret, environment = 'sandbox') {
    this.clientId = clientId;
    this.secret = secret;
    
    const configuration = new Configuration({
      basePath: PlaidEnvironments[environment],
      baseOptions: {
        headers: {
          'PLAID-CLIENT-ID': this.clientId,
          'PLAID-SECRET': this.secret,
        },
      },
    });

    this.client = new PlaidApi(configuration);
  }

  /**
   * Create a link token for Plaid Link initialization
   * @param {string} userId - User identifier
   * @param {string} clientName - Application name
   * @returns {Promise<Object>} Link token
   */
  async createLinkToken(userId, clientName = 'Cryptobeam Compliance') {
    try {
      const response = await this.client.linkTokenCreate({
        user: {
          client_user_id: userId,
        },
        client_name: clientName,
        products: ['auth', 'identity', 'transactions'],
        country_codes: ['US'],
        language: 'en',
      });

      return {
        linkToken: response.data.link_token,
        expiration: response.data.expiration,
      };
    } catch (error) {
      console.error('Failed to create link token:', error.message);
      throw new Error(`Link token creation failed: ${error.message}`);
    }
  }

  /**
   * Exchange public token for access token
   * @param {string} publicToken - Public token from Plaid Link
   * @returns {Promise<Object>} Access token and item ID
   */
  async exchangePublicToken(publicToken) {
    try {
      const response = await this.client.itemPublicTokenExchange({
        public_token: publicToken,
      });

      return {
        accessToken: response.data.access_token,
        itemId: response.data.item_id,
      };
    } catch (error) {
      console.error('Failed to exchange public token:', error.message);
      throw new Error(`Token exchange failed: ${error.message}`);
    }
  }

  /**
   * Get identity information for KYC verification
   * @param {string} accessToken - Plaid access token
   * @returns {Promise<Object>} Identity information
   */
  async getIdentity(accessToken) {
    try {
      const response = await this.client.identityGet({
        access_token: accessToken,
      });

      const accounts = response.data.accounts || [];
      const identities = [];

      accounts.forEach(account => {
        if (account.owners) {
          account.owners.forEach(owner => {
            identities.push({
              names: owner.names || [],
              emails: owner.emails?.map(e => e.data) || [],
              phoneNumbers: owner.phone_numbers?.map(p => p.data) || [],
              addresses: owner.addresses?.map(a => ({
                street: a.data.street,
                city: a.data.city,
                region: a.data.region,
                postalCode: a.data.postal_code,
                country: a.data.country,
              })) || [],
            });
          });
        }
      });

      return {
        identities: identities,
        verificationTimestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Failed to get identity:', error.message);
      throw new Error(`Identity retrieval failed: ${error.message}`);
    }
  }

  /**
   * Get account and routing numbers for verification
   * @param {string} accessToken - Plaid access token
   * @returns {Promise<Object>} Auth information
   */
  async getAuth(accessToken) {
    try {
      const response = await this.client.authGet({
        access_token: accessToken,
      });

      const accounts = response.data.accounts.map(account => ({
        accountId: account.account_id,
        name: account.name,
        type: account.type,
        subtype: account.subtype,
        routingNumber: response.data.numbers.ach?.find(n => n.account_id === account.account_id)?.routing,
        accountNumber: response.data.numbers.ach?.find(n => n.account_id === account.account_id)?.account,
      }));

      return {
        accounts: accounts,
        verificationTimestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Failed to get auth:', error.message);
      throw new Error(`Auth retrieval failed: ${error.message}`);
    }
  }

  /**
   * Get transaction history for AML monitoring
   * @param {string} accessToken - Plaid access token
   * @param {Date} startDate - Start date
   * @param {Date} endDate - End date
   * @returns {Promise<Object>} Transaction history
   */
  async getTransactions(accessToken, startDate, endDate) {
    try {
      const response = await this.client.transactionsGet({
        access_token: accessToken,
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
      });

      const transactions = response.data.transactions.map(txn => ({
        transactionId: txn.transaction_id,
        accountId: txn.account_id,
        amount: txn.amount,
        date: txn.date,
        name: txn.name,
        merchantName: txn.merchant_name,
        category: txn.category,
        pending: txn.pending,
        location: txn.location,
      }));

      return {
        transactions: transactions,
        totalTransactions: response.data.total_transactions,
        accounts: response.data.accounts,
      };
    } catch (error) {
      console.error('Failed to get transactions:', error.message);
      throw new Error(`Transaction retrieval failed: ${error.message}`);
    }
  }

  /**
   * Verify source of funds for compliance
   * @param {string} accessToken - Plaid access token
   * @returns {Promise<Object>} Source of funds verification
   */
  async verifySourceOfFunds(accessToken) {
    try {
      // Get recent transactions and account balances
      const endDate = new Date();
      const startDate = new Date();
      startDate.setMonth(startDate.getMonth() - 3); // Last 3 months

      const [transactions, auth] = await Promise.all([
        this.getTransactions(accessToken, startDate, endDate),
        this.getAuth(accessToken),
      ]);

      // Analyze transaction patterns
      const deposits = transactions.transactions.filter(t => t.amount < 0); // Negative amounts are deposits in Plaid
      const withdrawals = transactions.transactions.filter(t => t.amount > 0);

      const totalDeposits = deposits.reduce((sum, t) => sum + Math.abs(t.amount), 0);
      const totalWithdrawals = withdrawals.reduce((sum, t) => sum + t.amount, 0);

      return {
        verified: true,
        sourceOfFunds: {
          totalDeposits: totalDeposits,
          totalWithdrawals: totalWithdrawals,
          depositCount: deposits.length,
          withdrawalCount: withdrawals.length,
          netFlow: totalDeposits - totalWithdrawals,
        },
        accounts: auth.accounts,
        analysisTimestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Failed to verify source of funds:', error.message);
      throw new Error(`Source of funds verification failed: ${error.message}`);
    }
  }

  /**
   * Get account balances
   * @param {string} accessToken - Plaid access token
   * @returns {Promise<Object>} Balance information
   */
  async getBalances(accessToken) {
    try {
      const response = await this.client.accountsBalanceGet({
        access_token: accessToken,
      });

      const balances = response.data.accounts.map(account => ({
        accountId: account.account_id,
        name: account.name,
        type: account.type,
        balances: {
          available: account.balances.available,
          current: account.balances.current,
          limit: account.balances.limit,
          currency: account.balances.iso_currency_code,
        },
      }));

      return {
        balances: balances,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Failed to get balances:', error.message);
      throw new Error(`Balance retrieval failed: ${error.message}`);
    }
  }
}

module.exports = PlaidClient;
