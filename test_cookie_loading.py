#!/usr/bin/env python3
"""Test if cookie loading from storage_state.json is working."""

import json
from pathlib import Path

storage_path = Path("/Users/mladjanantic/Work/socialBot/data/browser_profiles/agent_1/storage_state.json")

print(f"File exists: {storage_path.exists()}")
print(f"File path: {storage_path}")

with open(storage_path, 'r') as f:
    state = json.load(f)

print(f"\nKeys in state: {state.keys()}")
print(f"Number of cookies: {len(state.get('cookies', []))}")
print(f"'cookies' key exists: {'cookies' in state}")

if 'cookies' in state:
    print(f"\nFirst 3 cookies:")
    for cookie in state['cookies'][:3]:
        print(f"  - {cookie['name']}: {cookie['value'][:20]}... (domain: {cookie['domain']})")
