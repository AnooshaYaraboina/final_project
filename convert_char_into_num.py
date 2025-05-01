import hashlib

import pandas as pd


def consistent_string_to_int(value):
    """Converts a string into a consistent integer using hashing."""
    if isinstance(value, str):  # Apply only to strings
        hash_object = hashlib.md5(value.encode())  
        return int(hash_object.hexdigest(), 16) % 10**8  # Convert hash to 8-digit integer
    return value  # Keep numbers unchanged

def process_dataframe(input_path, output_path):
    """Reads a dataset, converts string values to consistent integers, and saves the result."""
    # Load dataset (CSV or Excel)
    if input_path.endswith(".csv"):
        df = pd.read_csv(input_path)
    elif input_path.endswith(".xlsx"):
        df = pd.read_excel(input_path)
    else:
        print(" Unsupported file format. Use CSV or XLSX.")
        return
    
    # Apply transformation to all values in the dataset
    df_transformed = df.map(consistent_string_to_int)

    # Save processed dataset
    if output_path.endswith(".csv"):
        df_transformed.to_csv(output_path, index=False)
    elif output_path.endswith(".xlsx"):
        df_transformed.to_excel(output_path, index=False)
    
    print(f" Transformed dataset saved to: {output_path}")

# Example Usage
if __name__ == "__main__":
    input_file = "Book1.xlsx"
    output_file = "Book1_transformed.xlsx"
    process_dataframe(input_file, output_file)