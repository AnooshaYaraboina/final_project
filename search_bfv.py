import hashlib
import os
import time  #  For measuring execution time

import pandas as pd
import tenseal as ts

# 🔹 Load Data from Excel File
file_path = "C:/Temp/Book1_copy.xlsx"
if not os.path.exists(file_path):
    print(f" Error: '{file_path}' not found.")
    exit()

df = pd.read_excel(file_path)

# ✅ Ensure required columns exist
required_cols = ["S.No", "Student Name", "Student Roll Number"]
if not all(col in df.columns for col in required_cols):
    print(" Required columns not found in the Excel file.")
    exit()

# 🔹 Convert Names to Numeric using SHA-256
def hash_name(name):
    return int(hashlib.sha256(name.strip().lower().encode()).hexdigest(), 16) % 10**5  # 5-digit hash

df["Hashed_Name"] = df["Student Name"].apply(hash_name)

# 🔹 Create BFV Encryption Context
context = ts.context(
    ts.SCHEME_TYPE.BFV,
    poly_modulus_degree=8192,
    plain_modulus=1032193
)
secret_key = context.secret_key()
context.generate_galois_keys()
context.make_context_public()

# 🔹 Encrypt Hashed Names
df["Enc_Name"] = df["Hashed_Name"].apply(lambda x: ts.bfv_vector(context, [x]))

# 🔹 Get User Input for Search
query_input = input("Enter student name to search: ")
hashed_query = hash_name(query_input)
enc_query = ts.bfv_vector(context, [hashed_query])

# 🔍 Perform Homomorphic Search with Time Measurement
start_time = time.time()  # Start timer

match_found = False
for i in range(len(df)):
    enc_diff = df["Enc_Name"][i] - enc_query
    dec_diff = enc_diff.decrypt(secret_key)[0]
    
    if dec_diff == 0:
        end_time = time.time()  # Stop timer
        time_taken = end_time - start_time
        print(f"Match found: {df['Student Name'][i]} (Roll No: {df['Student Roll Number'][i]})")
        print(f"Time taken for search: {time_taken:.4f} seconds")
        match_found = True
        break

if not match_found:
    end_time = time.time()  # Stop timer even if no match is found
    time_taken = end_time - start_time
    print(f" '{query_input}' is NOT present in the dataset.")
    print(f" Time taken for search: {time_taken:.4f} seconds")
