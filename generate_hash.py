import hashlib

password = input("Enter your password: ")
hash_value = hashlib.sha256(password.encode()).hexdigest()
print(f"SHA-256 hash: {hash_value}")