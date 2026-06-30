# fix_encoding.py
import os

# Define the paths to your seed file
seed_path = r"swift_analytics\seeds\raw_concerts.csv"

print("Reading CSV with Windows encoding...")
# Read the file using the original Windows encoding that handles the '0x97' dash byte
with open(seed_path, "r", encoding="cp1252", errors="ignore") as source_file:
    content = source_file.read()

print("Re-writing CSV with clean UTF-8 encoding...")
# Overwrite the exact same file using strict standard UTF-8 encoding
with open(seed_path, "w", encoding="utf-8") as target_file:
    target_file.write(content)

print("Encoding successfully fixed!")