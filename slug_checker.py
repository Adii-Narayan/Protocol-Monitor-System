# slug_checker.py
import requests

def find_slug(name_fragment):
    try:
        resp = requests.get("https://api.llama.fi/protocols", timeout=5)
        resp.raise_for_status()
        slugs = [p["slug"] for p in resp.json() if name_fragment.lower() in p["name"].lower()]
        print(f"Matches for '{name_fragment}':", slugs)
        return slugs
    except Exception as e:
        print("❌ Error fetching protocol list:", e)
        return []

# 🔍 Try it out
find_slug("aave")
find_slug("uniswap")
find_slug("rocketpool")
find_slug("rocket")
