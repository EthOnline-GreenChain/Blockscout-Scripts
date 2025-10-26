import requests
import json
from datetime import datetime, timezone
import sys

sys.stdout.reconfigure(encoding="utf-8")

# === CONFIG ===
BLOCKSCOUT_API = "https://grenchain-ethglobal.cloud.blockscout.com/api"
TX_HASH = "0xd97e6cdbbc7bef4fc3193ad849b103dd23313b3bcf8b55d241c06748e262d50a"

# Default local mapping of known addresses → chain IDs
# You can expand this or fetch dynamically from a registry
ADDRESS_CHAIN_MAP = {
    "0x1e31bebd0970b143279cb873c6005791f0802bdf": "11155111",  # Sepolia (sender)
    "0xcac524bca292aaade2df8a05cc58f0a65b1b3bb9": "11155111",  # Contract (Sepolia)
    "0x8009fef9ba8bd6f87a09c4dccc85001e7875b0d7": "11155111",  # Org A wallet
    "0xfad8f1035ed8d097d354bb29c9e4714b5fc4566d": "1101"       # Org B on Polygon zkEVM (example)
}

# === FETCH TRANSACTION DATA ===
url = f"{BLOCKSCOUT_API}?module=transaction&action=gettxinfo&txhash={TX_HASH}"
resp = requests.get(url)
resp.raise_for_status()
data = resp.json()

if "result" not in data or not data["result"]:
    print("⚠️  No result field found in response.")
    data["result"] = {}

else:
    result = data["result"]

    # Add readable timestamp
    if "timeStamp" in result and result["timeStamp"].isdigit():
        ts = datetime.fromtimestamp(int(result["timeStamp"]), tz=timezone.utc)
        result["readable_time"] = ts.strftime("%Y-%m-%d %H:%M:%S UTC")

    # Determine from/to chain IDs
    from_addr = result.get("from", "").lower()
    to_addr = result.get("to", "").lower()

    result["fromChainId"] = ADDRESS_CHAIN_MAP.get(from_addr, "unknown")
    result["toChainId"] = ADDRESS_CHAIN_MAP.get(to_addr, "unknown")

    # Handle ERC20 transfers (decode from logs)
    logs = result.get("logs", [])
    transfers = []
    for log in logs:
        if log["topics"][0].startswith("0xddf252ad"):  # ERC20 Transfer event
            sender = "0x" + log["topics"][1][-40:]
            receiver = "0x" + log["topics"][2][-40:]
            amount = int(log["data"], 16)
            transfers.append({
                "from": sender,
                "fromChainId": ADDRESS_CHAIN_MAP.get(sender.lower(), "unknown"),
                "to": receiver,
                "toChainId": ADDRESS_CHAIN_MAP.get(receiver.lower(), "unknown"),
                "amount": amount
            })
    if transfers:
        result["tokenTransfers"] = transfers

    data["result"] = result

# === SAVE AS JSON ===
with open("transaction_multichain.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("✅ Multi-chain transaction saved to transaction_multichain.json")
