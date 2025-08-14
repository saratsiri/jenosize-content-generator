"""Debug API key issue"""
import os
from dotenv import load_dotenv

# Load environment variables
if os.getenv("ENVIRONMENT") != "production":
    load_dotenv()

print("=== API Key Debug ===")
claude_key = os.getenv("CLAUDE_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")

if claude_key:
    print(f"CLAUDE_API_KEY found: {claude_key[:15]}...{claude_key[-10:]} (length: {len(claude_key)})")
    print(f"First char: '{claude_key[0]}', Last char: '{claude_key[-1]}'")
    print(f"Contains newlines: {repr(claude_key) != claude_key}")
else:
    print("CLAUDE_API_KEY not found")

if anthropic_key:
    print(f"ANTHROPIC_API_KEY found: {anthropic_key[:15]}...{anthropic_key[-10:]} (length: {len(anthropic_key)})")
else:
    print("ANTHROPIC_API_KEY not found")

print("\nAll environment variables:")
for key, value in os.environ.items():
    if 'API' in key or 'KEY' in key:
        if value and len(value) > 10:
            print(f"{key}: {value[:10]}...{value[-5:]} (len: {len(value)})")
        else:
            print(f"{key}: {value}")