import requests
import json
from datetime import datetime, timezone
import sys

sys.stdout.reconfigure(encoding="utf-8")

# === CONFIG ===
BLOCKSCOUT_API = "https://grenchain-ethglobal.cloud.blockscout.com/api"
TX_HASH = "0xd97e6cdbbc7bef4fc3193ad849b103dd23313b3bcf8b55d241c06748e262d50a"

# Default local mapping of known addresses → chain IDs
ADDRESS_CHAIN_MAP = {
    "0x1e31bebd0970b143279cb873c6005791f0802bdf": "11155111",  # Sepolia (sender)
    "0xcac524bca292aaade2df8a05cc58f0a65b1b3bb9": "11155111",  # Contract (Sepolia)
    "0x8009fef9ba8bd6f87a09c4dccc85001e7875b0d7": "11155111",  # Org A wallet
    "0xfad8f1035ed8d097d354bb29c9e4714b5fc4566d": "1101"       # Org B on Polygon zkEVM
}

# ERC20/ERC721/ERC1155 Event Signatures
EVENT_SIGNATURES = {
    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef": "Transfer(address,address,uint256)",
    "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925": "Approval(address,address,uint256)",
    "0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62": "TransferSingle(address,address,address,uint256,uint256)",
    "0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb": "TransferBatch(address,address,address,uint256[],uint256[])"
}

def decode_address(topic_hex):
    """Extract address from topic (last 40 chars, prefix with 0x)"""
    return "0x" + topic_hex[-40:].lower()

def safe_int(value, default=0):
    """Safely convert hex or string to int"""
    try:
        if isinstance(value, str) and value.startswith("0x"):
            return int(value, 16)
        return int(value)
    except (ValueError, TypeError):
        return default

def wei_to_ether(wei_value):
    """Convert wei to ether"""
    return wei_value / 10**18

def fetch_transaction_receipt(tx_hash):
    """Fetch transaction receipt for additional details"""
    url = f"{BLOCKSCOUT_API}?module=transaction&action=gettxreceiptstatus&txhash={tx_hash}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json().get("result", {})
    except:
        return {}

def fetch_internal_transactions(tx_hash):
    """Fetch internal transactions"""
    url = f"{BLOCKSCOUT_API}?module=account&action=txlistinternal&txhash={tx_hash}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        result = resp.json().get("result", [])
        return result if isinstance(result, list) else []
    except:
        return []

def fetch_contract_abi(address):
    """Fetch contract ABI if verified"""
    url = f"{BLOCKSCOUT_API}?module=contract&action=getabi&address={address}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        result = resp.json().get("result")
        return json.loads(result) if result else None
    except:
        return None

def fetch_token_info(address):
    """Fetch token information"""
    url = f"{BLOCKSCOUT_API}?module=token&action=getToken&contractaddress={address}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json().get("result", {})
    except:
        return {}

# === FETCH MAIN TRANSACTION DATA ===
print(f"🔍 Fetching transaction: {TX_HASH}\n")
url = f"{BLOCKSCOUT_API}?module=transaction&action=gettxinfo&txhash={TX_HASH}"
resp = requests.get(url)
resp.raise_for_status()
data = resp.json()

if "result" not in data or not data["result"]:
    print("⚠️  No result field found in response.")
    data["result"] = {}
    sys.exit(1)

result = data["result"]

# === ENHANCED TRANSACTION DETAILS ===
enhanced_tx = {
    # Core Transaction Fields
    "hash": result.get("hash"),
    "blockNumber": safe_int(result.get("blockNumber")),
    "blockHash": result.get("blockHash"),
    "transactionIndex": safe_int(result.get("transactionIndex")),
    "timestamp": safe_int(result.get("timeStamp")),
    
    # Addresses & Chain Info
    "from": result.get("from", "").lower(),
    "fromChainId": ADDRESS_CHAIN_MAP.get(result.get("from", "").lower(), "unknown"),
    "to": result.get("to", "").lower() if result.get("to") else None,
    "toChainId": ADDRESS_CHAIN_MAP.get(result.get("to", "").lower(), "unknown") if result.get("to") else None,
    "contractAddress": result.get("contractAddress", "").lower() if result.get("contractAddress") else None,
    
    # Value & Gas
    "value": safe_int(result.get("value")),
    "valueEther": wei_to_ether(safe_int(result.get("value"))),
    "gas": safe_int(result.get("gas")),
    "gasPrice": safe_int(result.get("gasPrice")),
    "gasPriceGwei": safe_int(result.get("gasPrice")) / 10**9,
    "gasUsed": safe_int(result.get("gasUsed")),
    "effectiveGasPrice": safe_int(result.get("effectiveGasPrice", result.get("gasPrice"))),
    "cumulativeGasUsed": safe_int(result.get("cumulativeGasUsed")),
    "txnFee": safe_int(result.get("gasUsed")) * safe_int(result.get("gasPrice")),
    "txnFeeEther": wei_to_ether(safe_int(result.get("gasUsed")) * safe_int(result.get("gasPrice"))),
    
    # Transaction Type & Data
    "type": safe_int(result.get("type", "0x0")),
    "nonce": safe_int(result.get("nonce")),
    "input": result.get("input", "0x"),
    "methodId": result.get("input", "0x")[:10] if result.get("input", "0x") != "0x" else None,
    "functionName": result.get("functionName"),
    
    # Status & Confirmations
    "status": "success" if result.get("isError") == "0" or result.get("txreceipt_status") == "1" else "failed",
    "isError": result.get("isError"),
    "errCode": result.get("errCode"),
    "confirmations": safe_int(result.get("confirmations")),
    
    # EIP-1559 Fields (if applicable)
    "maxFeePerGas": safe_int(result.get("maxFeePerGas")) if result.get("maxFeePerGas") else None,
    "maxPriorityFeePerGas": safe_int(result.get("maxPriorityFeePerGas")) if result.get("maxPriorityFeePerGas") else None,
    "baseFeePerGas": safe_int(result.get("baseFeePerGas")) if result.get("baseFeePerGas") else None,
    
    # Signature Components
    "v": result.get("v"),
    "r": result.get("r"),
    "s": result.get("s"),
    
    # Additional Metadata
    "logs": [],
    "tokenTransfers": [],
    "internalTransactions": [],
    "decodedInput": None,
}

# Add readable timestamp
if enhanced_tx["timestamp"]:
    ts = datetime.fromtimestamp(enhanced_tx["timestamp"], tz=timezone.utc)
    enhanced_tx["readableTime"] = ts.strftime("%Y-%m-%d %H:%M:%S UTC")
    enhanced_tx["dateOnly"] = ts.strftime("%Y-%m-%d")
    enhanced_tx["timeOnly"] = ts.strftime("%H:%M:%S UTC")

# === PROCESS LOGS & TOKEN TRANSFERS ===
logs = result.get("logs", [])
token_contracts = set()

for log in logs:
    topics = log.get("topics", [])
    if not topics:
        continue
    
    event_sig = topics[0]
    log_entry = {
        "address": log.get("address", "").lower(),
        "topics": topics,
        "data": log.get("data"),
        "logIndex": safe_int(log.get("logIndex")),
        "blockNumber": safe_int(log.get("blockNumber")),
        "eventSignature": event_sig,
        "eventName": EVENT_SIGNATURES.get(event_sig, "Unknown")
    }
    enhanced_tx["logs"].append(log_entry)
    
    # Decode ERC20 Transfer Events
    if event_sig.startswith("0xddf252ad"):  # Transfer(address,address,uint256)
        if len(topics) >= 3:
            sender = decode_address(topics[1])
            receiver = decode_address(topics[2])
            amount = safe_int(log.get("data"))
            
            token_addr = log.get("address", "").lower()
            token_contracts.add(token_addr)
            
            transfer = {
                "type": "ERC20",
                "tokenContract": token_addr,
                "from": sender,
                "fromChainId": ADDRESS_CHAIN_MAP.get(sender, "unknown"),
                "to": receiver,
                "toChainId": ADDRESS_CHAIN_MAP.get(receiver, "unknown"),
                "amount": amount,
                "amountFormatted": amount / 10**18,  # Assuming 18 decimals
                "logIndex": safe_int(log.get("logIndex"))
            }
            enhanced_tx["tokenTransfers"].append(transfer)
    
    # Decode ERC20 Approval Events
    elif event_sig.startswith("0x8c5be1e5"):  # Approval(address,address,uint256)
        if len(topics) >= 3:
            owner = decode_address(topics[1])
            spender = decode_address(topics[2])
            amount = safe_int(log.get("data"))
            
            log_entry["decodedEvent"] = {
                "type": "Approval",
                "owner": owner,
                "spender": spender,
                "amount": amount
            }

# === FETCH TOKEN METADATA ===
for token_addr in token_contracts:
    token_info = fetch_token_info(token_addr)
    if token_info:
        for transfer in enhanced_tx["tokenTransfers"]:
            if transfer["tokenContract"] == token_addr:
                transfer["tokenName"] = token_info.get("name")
                transfer["tokenSymbol"] = token_info.get("symbol")
                transfer["tokenDecimals"] = safe_int(token_info.get("decimals", 18))
                # Recalculate formatted amount with correct decimals
                transfer["amountFormatted"] = transfer["amount"] / (10 ** transfer["tokenDecimals"])

# === FETCH INTERNAL TRANSACTIONS ===
print("📥 Fetching internal transactions...")
internal_txs = fetch_internal_transactions(TX_HASH)
for itx in internal_txs:
    enhanced_tx["internalTransactions"].append({
        "from": itx.get("from", "").lower(),
        "to": itx.get("to", "").lower(),
        "value": safe_int(itx.get("value")),
        "valueEther": wei_to_ether(safe_int(itx.get("value"))),
        "type": itx.get("type"),
        "gas": safe_int(itx.get("gas")),
        "gasUsed": safe_int(itx.get("gasUsed")),
        "isError": itx.get("isError"),
        "errCode": itx.get("errCode")
    })

# === FETCH CONTRACT INFO ===
if enhanced_tx["to"] and enhanced_tx["to"] != "0x0000000000000000000000000000000000000000":
    print(f"📜 Fetching contract info for {enhanced_tx['to']}...")
    abi = fetch_contract_abi(enhanced_tx["to"])
    if abi:
        enhanced_tx["contractABI"] = abi
        enhanced_tx["isVerifiedContract"] = True
    else:
        enhanced_tx["isVerifiedContract"] = False

# === TRANSACTION CLASSIFICATION ===
if enhanced_tx["to"] is None:
    enhanced_tx["txType"] = "Contract Deployment"
elif enhanced_tx["value"] > 0 and not enhanced_tx["tokenTransfers"]:
    enhanced_tx["txType"] = "ETH Transfer"
elif enhanced_tx["tokenTransfers"]:
    enhanced_tx["txType"] = "Token Transfer"
elif enhanced_tx["input"] != "0x":
    enhanced_tx["txType"] = "Contract Interaction"
else:
    enhanced_tx["txType"] = "Unknown"

# === SUMMARY STATISTICS ===
enhanced_tx["summary"] = {
    "totalETHTransferred": enhanced_tx["valueEther"],
    "totalTokenTransfers": len(enhanced_tx["tokenTransfers"]),
    "totalInternalTransactions": len(enhanced_tx["internalTransactions"]),
    "totalLogs": len(enhanced_tx["logs"]),
    "totalGasCost": enhanced_tx["txnFeeEther"],
    "isMultiChain": len(set([t["fromChainId"] for t in enhanced_tx["tokenTransfers"]] + 
                            [t["toChainId"] for t in enhanced_tx["tokenTransfers"]])) > 1
}

# === SAVE AS JSON ===
output_file = "transaction_enhanced.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(enhanced_tx, f, indent=4, ensure_ascii=False)

# === PRINT SUMMARY ===
print(f"\n✅ Enhanced transaction data saved to {output_file}\n")
print("=" * 60)
print("📊 TRANSACTION SUMMARY")
print("=" * 60)
print(f"Hash:              {enhanced_tx['hash']}")
print(f"Block:             #{enhanced_tx['blockNumber']}")
print(f"Type:              {enhanced_tx['txType']}")
print(f"Status:            {enhanced_tx['status'].upper()}")
print(f"Timestamp:         {enhanced_tx.get('readableTime', 'N/A')}")
print(f"From:              {enhanced_tx['from']}")
print(f"To:                {enhanced_tx['to'] or 'Contract Creation'}")
print(f"Value:             {enhanced_tx['valueEther']:.6f} ETH")
print(f"Gas Used:          {enhanced_tx['gasUsed']:,} / {enhanced_tx['gas']:,}")
print(f"Gas Price:         {enhanced_tx['gasPriceGwei']:.4f} Gwei")
print(f"Txn Fee:           {enhanced_tx['txnFeeEther']:.8f} ETH")
print(f"Token Transfers:   {len(enhanced_tx['tokenTransfers'])}")
print(f"Internal Txns:     {len(enhanced_tx['internalTransactions'])}")
print(f"Logs:              {len(enhanced_tx['logs'])}")
print("=" * 60)

# Print token transfers
if enhanced_tx["tokenTransfers"]:
    print("\n🪙 TOKEN TRANSFERS:")
    for i, transfer in enumerate(enhanced_tx["tokenTransfers"], 1):
        symbol = transfer.get("tokenSymbol", "???")
        amount = transfer.get("amountFormatted", 0)
        print(f"  {i}. {amount:.6f} {symbol}")
        print(f"     From: {transfer['from']} (Chain: {transfer['fromChainId']})")
        print(f"     To:   {transfer['to']} (Chain: {transfer['toChainId']})")

print("\n✨ Complete data available in transaction_enhanced.json")