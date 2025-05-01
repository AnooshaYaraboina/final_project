import os
import pickle
import sys

import numpy as np
import pandas as pd
import tenseal as ts

# Folder to store encrypted files
ENCRYPTED_FOLDER = "encrypted_data"
os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)

def create_bfv_context():
    """Creates and saves a BFV encryption context for future use."""
    context = ts.context(
        ts.SCHEME_TYPE.BFV, 
        poly_modulus_degree=8192, 
        plain_modulus=1032193
    )
    
    context.generate_galois_keys()
    context.make_context_public()  

    # Save context for future encryption
    context_path = os.path.join(ENCRYPTED_FOLDER, "bfv_context.pkl")
    with open(context_path, "wb") as f:
        f.write(context.serialize())  #  Proper serialization

    print(f" BFV encryption context and keys saved successfully in {context_path}.")
    return context

def encrypt_file(input_path, output_file=os.path.join(ENCRYPTED_FOLDER, "encrypted_data.pkl")):
    """Encrypts numerical data from a CSV or Excel file using TenSEAL and BFV encryption."""
    
    if not os.path.exists(input_path):
        print(f" Error: File '{input_path}' not found.")
        return
    
    # Load BFV context
    try:
        context_path = os.path.join(ENCRYPTED_FOLDER, "bfv_context.pkl")
        with open(context_path, "rb") as f:
            context = ts.context_from(f.read())  #  Proper deserialization
        print(" Encryption context loaded successfully.")
    except Exception as e:
        print(f" Error loading encryption context: {e}")
        return
    
    # Read input file
    try:
        if input_path.endswith(".csv"):
            df = pd.read_csv(input_path)
        elif input_path.endswith(".xlsx"):
            df = pd.read_excel(input_path)
        else:
            print(" Error: Unsupported file format. Use CSV or XLSX.")
            return

        print(f" Successfully loaded file: {input_path}")
    except Exception as e:
        print(f" Error reading file: {e}")
        return
    
    encrypted_data = []
    
    try:
        # Encrypt each row
        for _, row in df.iterrows():
            numeric_values = row.tolist()  
            numeric_values = [int(value) for value in numeric_values]  
            encrypted_row = ts.bfv_vector(context, numeric_values)  
            encrypted_data.append(encrypted_row.serialize())  #  Use serialization
        
        # Save encrypted data properly
        with open(output_file, "wb") as f:
            pickle.dump(encrypted_data, f)

        print(f" Encrypted data stored successfully in: {output_file}")
    
    except Exception as e:
        print(f" Error during encryption: {e}")

# Command-line execution
if __name__ == "_main_":
    if len(sys.argv) < 2:
        print(" Error: No input file provided. Usage: python script.py <file_path>")
    else:
        input_file_path = sys.argv[1]  
        create_bfv_context()  
        encrypt_file(input_file_path)