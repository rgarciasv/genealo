import json
import os
import sys

CORPUS_PATH = r"c:\TRABAJOS\personal\genealo\catalogo_corpus.json"

def main():
    with open(CORPUS_PATH, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    print("Data type:", type(data))
    if isinstance(data, dict):
        print("Keys:", list(data.keys()))
        for k, v in data.items():
            if isinstance(v, list):
                print(f"Key '{k}': list with {len(v)} items")
            elif isinstance(v, dict):
                print(f"Key '{k}': dict with {len(v)} keys")
            else:
                print(f"Key '{k}': {type(v)}")
    elif isinstance(data, list):
        print(f"Data is list of {len(data)} items")
        if data:
            print("Item 0 keys:", list(data[0].keys()) if isinstance(data[0], dict) else type(data[0]))

if __name__ == "__main__":
    main()
