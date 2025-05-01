import tenseal as ts
import time
import tempfile
import os
import pickle
import matplotlib.pyplot as plt
import numpy as np
import sys

def benchmark(operation, *args, repeat=3):
    durations = []
    for _ in range(repeat):
        start = time.time()
        operation(*args)
        durations.append(time.time() - start)
    return sum(durations) / repeat

def simulate_search(enc_data, enc_query, secret_key, is_ckks=False):
    for v in enc_data:
        diff = v - enc_query
        dec = diff.decrypt(secret_key)[0]
        if is_ckks:
            if abs(dec) < 1e-3:
                break
        else:
            if dec == 0:
                break

def measure_file_size(obj):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        pickle.dump(obj, temp_file)
        temp_file_path = temp_file.name
    size_kb = os.path.getsize(temp_file_path) / 1024
    os.unlink(temp_file_path)
    return size_kb

def estimate_memory_size(enc_data):
    # Rough estimate of memory size in MB (for visual analysis)
    total_size = sum(sys.getsizeof(v) for v in enc_data)
    return total_size / (1024 * 1024)

results = {
    "Scheme": [],
    "EncryptTime": [],
    "DecryptTime": [],
    "SearchTime": [],
    "EncFileSize_KB": [],
    "InMemorySize_MB": []
}

# ======== Dataset ========
dataset = [i for i in range(100)]

# ======== BFV ========
bfv_context = ts.context(
    ts.SCHEME_TYPE.BFV, 
    poly_modulus_degree=8192, 
    plain_modulus=1032193
)
bfv_context.generate_galois_keys()
bfv_secret = bfv_context.secret_key()
bfv_context.make_context_public()

start = time.time()
enc_bfv = [ts.bfv_vector(bfv_context, [x]) for x in dataset]
encrypt_time = time.time() - start

decrypt_time = benchmark(lambda v: v.decrypt(bfv_secret)[0], enc_bfv[0])
search_time = benchmark(simulate_search, enc_bfv, ts.bfv_vector(bfv_context, [50]), bfv_secret, False)
file_size_bfv = measure_file_size([v.serialize() for v in enc_bfv])
memory_bfv = estimate_memory_size(enc_bfv)

results["Scheme"].append("BFV")
results["EncryptTime"].append(encrypt_time)
results["DecryptTime"].append(decrypt_time)
results["SearchTime"].append(search_time)
results["EncFileSize_KB"].append(file_size_bfv)
results["InMemorySize_MB"].append(memory_bfv)

# ======== CKKS ========
ckks_context = ts.context(
    ts.SCHEME_TYPE.CKKS, 
    poly_modulus_degree=8192, 
    coeff_mod_bit_sizes=[60, 40, 60]
)
ckks_context.global_scale = 2**40
ckks_context.generate_galois_keys()
ckks_secret = ckks_context.secret_key()
ckks_context.make_context_public()

start = time.time()
enc_ckks = [ts.ckks_vector(ckks_context, [float(x)]) for x in dataset]
encrypt_time = time.time() - start

decrypt_time = benchmark(lambda v: v.decrypt(ckks_secret)[0], enc_ckks[0])
search_time = benchmark(simulate_search, enc_ckks, ts.ckks_vector(ckks_context, [50.0]), ckks_secret, True)
file_size_ckks = measure_file_size([v.serialize() for v in enc_ckks])
memory_ckks = estimate_memory_size(enc_ckks)

results["Scheme"].append("CKKS")
results["EncryptTime"].append(encrypt_time)
results["DecryptTime"].append(decrypt_time)
results["SearchTime"].append(search_time)
results["EncFileSize_KB"].append(file_size_ckks)
results["InMemorySize_MB"].append(memory_ckks)

# ======== Charts ========
x = np.arange(len(results["Scheme"]))
width = 0.2

# ⏱️ Time Comparison
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x - width, results["EncryptTime"], width, label='Encryption Time (s)')
ax.bar(x, results["SearchTime"], width, label='Search Time (s)')
ax.bar(x + width, results["DecryptTime"], width, label='Decryption Time (s)')
ax.set_xticks(x)
ax.set_xticklabels(results["Scheme"])
ax.set_ylabel("Time (seconds)")
ax.set_title("FHE Scheme Timing Comparison")
ax.legend()
plt.grid(True, axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# 💾 Size Comparison
fig, ax = plt.subplots(figsize=(10, 5))
bar1 = ax.bar(x - width/2, results["EncFileSize_KB"], width, label="Serialized File Size (KB)")
bar2 = ax.bar(x + width/2, results["InMemorySize_MB"], width, label="In-Memory Size (MB)")
ax.set_xticks(x)
ax.set_xticklabels(results["Scheme"])
ax.set_ylabel("Size")
ax.set_title("Encrypted Data Size Comparison")
ax.legend()
plt.grid(True, axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# 📋 Final Summary
print("\n Performance & Size Summary:")
for i in range(2):
    print(f"\n🔹 Scheme: {results['Scheme'][i]}")
    print(f"   •  Encryption Time:    {results['EncryptTime'][i]:.4f} s")
    print(f"   •  Decryption Time:    {results['DecryptTime'][i]:.6f} s")
    print(f"   •  Search Time:        {results['SearchTime'][i]:.6f} s")
    print(f"   •  Serialized Size:    {results['EncFileSize_KB'][i]:.2f} KB")
    print(f"   •  In-Memory Size:     {results['InMemorySize_MB'][i]:.2f} MB")
