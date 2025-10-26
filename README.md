# 🧭 Blockscout Integration Guide

This document explains how **Blockscout** is used within the GreenChain ecosystem to **visualize, verify, and interact with on-chain transactions** for organizations, tokens, and smart contracts.

---

## 🌍 Overview

[Blockscout](https://www.blockscout.com/) is an **open-source blockchain explorer** that allows anyone to view transactions, tokens, addresses, and smart contract details for any EVM-compatible chain.

GreenChain uses a **dedicated Blockscout instance** to:

- View organization token flows (Org A → Org B)
- Monitor transactions in real time
- Verify smart contracts
- Integrate explorer data into dashboards and SDKs

Instance URL:  
👉 **[https://grenchain-ethglobal.cloud.blockscout.com](https://grenchain-ethglobal.cloud.blockscout.com)**

---

## ⚙️ Instance Configuration

When launching your instance via [Autoscout](https://autoscout.blockscout.com/), you configure:

| Parameter                    | Example                    | Description                            |
| ---------------------------- | -------------------------- | -------------------------------------- |
| **Instance name\***          | `grenchain-ethglobal`      | Label for your instance (used in URL)  |
| **Chain name**               | `GreenChain`               | Display name of your custom chain      |
| **Chain ID**                 | `11155111`                 | EVM chain identifier                   |
| **HTTP RPC URL\***           | `https://rpc.grenchain.io` | Your node's archive RPC endpoint       |
| **WS URL**                   | `wss://ws.grenchain.io`    | WebSocket endpoint (optional)          |
| **Gas token symbol**         | `GRN`                      | Your native gas token                  |
| **Mainnet/Testnet**          | `Testnet`                  | Chain environment type                 |
| **Node type**                | `Geth`                     | Client type for indexing               |
| **WalletConnect project ID** | _Optional_                 | Enables transaction signing from dApps |

---

## 🧱 Using the Blockscout API

Blockscout exposes a familiar **Etherscan-style REST API**, available at:

```
https://grenchain-ethglobal.cloud.blockscout.com/api
```

---

## 🔍 Audit Trail Dashboard

GreenChain features a **comprehensive audit dashboard** built with Streamlit that integrates with both **Firebase Firestore** and **Blockscout** to track and verify carbon credit transactions.

### 📊 Dashboard Features

The GreenChain Audit Dashboard provides:

- **Real-time transaction monitoring** from Firestore
- **Organization-based transaction grouping** by sending wallet
- **Carbon credit tracking** with token transfer analysis
- **Verification workflow** for approving transactions
- **Detailed transaction history** with Blockscout integration

### 🏗️ Architecture

The audit system consists of three main components:

1. **Firebase Firestore Collections**:

   - `transactions`: Stores blockchain transaction data including hash, sender, receiver, value, and token transfers
   - `organizations`: Maps wallet addresses to organization names

2. **Data Aggregation**:

   - Groups transactions by sending wallet address
   - Calculates total ETH spent per organization
   - Sums carbon credits (CC) purchased via token transfers
   - Links wallet addresses to human-readable organization names

3. **Verification Interface**:
   - Displays transaction details including destination addresses
   - Shows ETH value and carbon credit amounts
   - Provides approval mechanism for auditors

### 📋 Transaction Data Structure

Each transaction record contains:

| Field            | Description                               |
| ---------------- | ----------------------------------------- |
| `hash`           | Transaction hash (viewable on Blockscout) |
| `from`           | Sending wallet address (organization)     |
| `to`             | Receiving wallet/contract address         |
| `value`          | ETH amount transferred                    |
| `readable_time`  | Human-readable timestamp                  |
| `success`        | Transaction status (success/failure)      |
| `tokenTransfers` | Array of carbon credit token transfers    |

### 🌱 Carbon Credit Tracking

The dashboard specifically tracks:

- **Total Crypto Spent**: Aggregate ETH value across all transactions per organization
- **Total Carbon Credits Purchased**: Sum of all token transfer amounts (CC)
- **Net Summary**: Provides ratio of credits to crypto spent

### 🔐 Audit Workflow

1. **Fetch Transactions**: Retrieve all transaction records from Firestore
2. **Group by Sender**: Aggregate transactions by sending wallet address
3. **Resolve Organization**: Map wallet addresses to organization names
4. **Display Overview**: Show detailed transaction table with:
   - Transaction hash (linkable to Blockscout)
   - Destination address
   - ETH value
   - Timestamp
   - Success status
   - Carbon credits transferred
5. **Approve**: Auditors can approve verified transaction batches

### 🔗 Blockscout Integration

Each transaction hash in the dashboard can be viewed on Blockscout by navigating to:

```
https://grenchain-ethglobal.cloud.blockscout.com/tx/[TRANSACTION_HASH]
```

This provides:

- Complete transaction details
- Smart contract interactions
- Token transfer logs
- Gas usage and fees
- Block confirmation status

---

## 🚀 Getting Started with Audit Dashboard

To run the audit dashboard locally:

```bash
# Install dependencies
pip install streamlit pandas firebase-admin

# Configure Firebase credentials in .streamlit/secrets.toml
# Run the dashboard
streamlit run audit_dashboard.py
```

### Required Firebase Secrets

Add to `.streamlit/secrets.toml`:

```toml
[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

---

## 📈 Future Enhancements

Planned improvements for the audit system:

- **Direct Blockscout API integration** for real-time transaction fetching
- **Automated verification** using smart contract events
- **Multi-signature approval** workflow
- **Export functionality** for compliance reporting
- **Historical analytics** and trend visualization
- **Alert system** for suspicious transactions

---

## 🤝 Contributing

For questions or contributions to the audit dashboard, please refer to the main GreenChain repository.
