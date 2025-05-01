import hashlib
import os
import pickle

import tenseal as ts

# 🔹 Paths to stored encryption context & encrypted data
ENCRYPTION_FOLDER = "D:/projecthomo/encrypted_data"
CONTEXT_FILE = os.path.join(ENCRYPTION_FOLDER, "bfv_context.pkl")
ENCRYPTED_FILE = os.path.join(ENCRYPTION_FOLDER, "encrypted_data.pkl")

# 🔹 Convert String into Consistent Numeric Hash
def consistent_string_to_int(value):
    """Converts a string into a consistent integer using hashing."""
    if isinstance(value, str):  # Apply only to strings
        value = value.strip().lower()  # Normalize input
        hash_object = hashlib.md5(value.encode())  
        return int(hash_object.hexdigest(), 16) % 10**8  # 8-digit numeric hash
    return value  # Keep numbers unchanged

# 🔹 Load Encryption Context (Public Only)
def load_encryption_context():
    """Loads the BFV encryption context from the stored file."""
    if not os.path.exists(CONTEXT_FILE):
        print(" Error: Encryption context file not found.")
        return None

    with open(CONTEXT_FILE, "rb") as f:
        return ts.context_from(pickle.load(f))

# 🔹 Encrypt Value Using Public Key
def encrypt_value(context, value):
    """Encrypts an integer value using the public encryption context."""
    return ts.bfv_vector(context, [value])  # Single-value encryption

# 🔹 Load Encrypted Data Safely
def load_encrypted_data():
    """Loads stored encrypted values and ensures dictionary format."""
    if not os.path.exists(ENCRYPTED_FILE):
        print(" Error: Encrypted data file not found.")
        return {}

    with open(ENCRYPTED_FILE, "rb") as f:
        stored_data = pickle.load(f)

    if isinstance(stored_data, dict):
        return stored_data  # ✅ Correct format
    elif isinstance(stored_data, list):
        print("Warning: Encrypted data is stored as a list. Converting to dictionary...")
        return {i: val for i, val in enumerate(stored_data)}  # Convert list to dict
    else:
        print("❌ Error: Unexpected format in encrypted data file!")
        return {}

# 🔹 Search for a Match Without Decryption
def search_value(user_input):
    """Encrypts the user input and checks for a match in stored encrypted values."""
    context = load_encryption_context()
    if not context:
        return

    # Hash & Encrypt User Input
    numeric_value = consistent_string_to_int(user_input)
    enc_user_value = encrypt_value(context, numeric_value)

    # Load Stored Encrypted Data
    stored_data = load_encrypted_data()
    if not stored_data:
        print("❌ No encrypted data available.")
        return

    # Homomorphic Subtraction for Matching
    for key, enc_stored_value in stored_data.items():
        try:
            encrypted_diff = enc_stored_value - enc_user_value  # Homomorphic subtraction
            decrypted_diff = encrypted_diff.decrypt()  # Requires secret key
            
            if decrypted_diff[0] == 0:
                print(f" Match Found for '{user_input}'!")
                return
        except Exception as e:
            print(f"⚠ Decryption error: {e}")

    print(f" No match found for '{user_input}'.")

# 🔹 Run the Search
if __name__ == "_main_":
    user_input = input("Enter value to search: ")
    search_value(user_input)