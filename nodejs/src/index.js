/**
 * Compliance API Server
 * Main Express application for AML/KYC/Sanctions compliance services
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
require('dotenv').config();

const app = express();

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(morgan('combined'));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'Cryptobeam Compliance API'
  });
});

// API routes
app.use('/api/sanctions', require('./routes/sanctions'));
app.use('/api/aml', require('./routes/aml'));
app.use('/api/kyc', require('./routes/kyc'));
app.use('/api/custody', require('./routes/custody'));

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(err.status || 500).json({
    error: {
      message: err.message || 'Internal server error',
      status: err.status || 500
    }
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: {
      message: 'Endpoint not found',
      status: 404
    }
  });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Compliance API server running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
});

module.exports = app;
