import hashlib

password = "n2351447"
hash_value = hashlib.sha256(password.encode()).hexdigest()
print(f"New password hash: {hash_value}")