import hashlib
import os
import time  # 🕒 Import time module

import pandas as pd
import tenseal as ts

# 🔹 Load Data
file_path = "C:/Temp/Book1_copy.xlsx"
if not os.path.exists(file_path):
    print(f" Error: '{file_path}' not found.")
    exit()

df = pd.read_excel(file_path)

# 🔹 Ensure required columns exist
required_cols = ["S.No", "Student Name", "Student Roll Number"]
if not all(col in df.columns for col in required_cols):
    print(" Required columns not found.")
    exit()

# 🔹 Convert Names to Float (via hash)
def hash_to_float(name):
    return float(int(hashlib.sha256(name.strip().lower().encode()).hexdigest(), 16) % 10**5)

df["Hashed_Name"] = df["Student Name"].apply(hash_to_float)

# 🔹 Create CKKS Context
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)
context.global_scale = 2**40
context.generate_galois_keys()
secret_key = context.secret_key()

# 🔹 Encrypt using CKKS
df["Enc_Name"] = df["Hashed_Name"].apply(lambda x: ts.ckks_vector(context, [x]))

# 🔹 Get User Input for Search
query = input("Enter student name to search: ")
query_hashed = hash_to_float(query)
enc_query = ts.ckks_vector(context, [query_hashed])

#  Approximate Search using CKKS
match_found = False
tolerance = 1e-3  # adjust based on use case

#  Start timing
start_time = time.time()

for i in range(len(df)):
    diff = df["Enc_Name"][i] - enc_query
    dec_diff = diff.decrypt(secret_key)[0]
    
    if abs(dec_diff) < tolerance:
        print(f" Match found: {df['Student Name'][i]} (Roll No: {df['Student Roll Number'][i]})")
        match_found = True
        break

#  End timing
end_time = time.time()
elapsed_time = end_time - start_time

if not match_found:
    print(f" '{query}' not found in the dataset.")

print(f" Search completed in {elapsed_time:.4f} seconds.")
