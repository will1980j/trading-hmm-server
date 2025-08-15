import hashlib

target_hash = "ee8afe1b663f1f07dd8e1322f033b3e27472f9e6b55889ce2c3ed56200c9f022"

# Common password variations to test
passwords = [
    "tradingempire25",
    "TradingEmpire25", 
    "tradingEmpire25",
    "TRADINGEMPIRE25",
    "trading_empire_25",
    "Trading_Empire_25",
    "tradingempire123",
    "TradingEmpire123",
    "trading123",
    "Trading123",
    "empire25",
    "Empire25",
    "changeme123"
]

print(f"Looking for password that generates hash: {target_hash}")
print()

for password in passwords:
    hash_value = hashlib.sha256(password.encode()).hexdigest()
    if hash_value == target_hash:
        print(f"FOUND IT! Password: '{password}'")
        break
    else:
        print(f"No match: '{password}' -> {hash_value}")

print("\nIf no match found, you'll need to set a new password.")