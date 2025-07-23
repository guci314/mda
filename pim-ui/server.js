const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Handle favicon requests
app.get('/favicon.ico', (req, res) => {
    res.status(204).end();
});

// Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/models', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'models.html'));
});

app.get('/instances', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'instances.html'));
});

app.get('/dashboard', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

app.get('/debug', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'debug.html'));
});

// API configuration endpoint
app.get('/api/config', (req, res) => {
    res.json({
        apiBaseUrl: API_BASE_URL
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`PIM UI Server running on http://localhost:${PORT}`);
    console.log(`Configured to connect to PIM Engine at: ${API_BASE_URL}`);
});