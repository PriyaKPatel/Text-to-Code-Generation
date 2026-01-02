#!/usr/bin/env python3
"""
Download and save CodeT5 model for offline use
"""
from transformers import T5ForConditionalGeneration, RobertaTokenizer
import os

# Set cache directory
cache_dir = "./models/codet5-base"
os.makedirs(cache_dir, exist_ok=True)

print("Downloading CodeT5-base model...")
model = T5ForConditionalGeneration.from_pretrained("Salesforce/codet5-base")
print("Downloading CodeT5-base tokenizer...")
tokenizer = RobertaTokenizer.from_pretrained("Salesforce/codet5-base")

print(f"Saving to {cache_dir}...")
model.save_pretrained(cache_dir)
tokenizer.save_pretrained(cache_dir)

print("✅ Model saved successfully!")
print(f"Model location: {os.path.abspath(cache_dir)}")
print("\nFiles saved:")
for file in os.listdir(cache_dir):
    print(f"  - {file}")

