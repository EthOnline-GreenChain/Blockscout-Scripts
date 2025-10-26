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
| **HTTP RPC URL\***           | `https://rpc.grenchain.io` | Your node’s archive RPC endpoint       |
| **WS URL**                   | `wss://ws.grenchain.io`    | WebSocket endpoint (optional)          |
| **Gas token symbol**         | `GRN`                      | Your native gas token                  |
| **Mainnet/Testnet**          | `Testnet`                  | Chain environment type                 |
| **Node type**                | `Geth`                     | Client type for indexing               |
| **WalletConnect project ID** | _Optional_                 | Enables transaction signing from dApps |

---

## 🧱 Using the Blockscout API

Blockscout exposes a familiar **Etherscan-style REST API**, available at:
