from snapshot import fetch_proposals

for space in ["uniswap.eth", "rocketpool.eth", "ens.eth"]:
    print(f"🔍 Testing {space}")
    proposals = fetch_proposals(space, 5)
    if proposals:
        for p in proposals:
            print(f"{p['title']} | {p['state']} | {p['start']} → {p['end']}")
        print("\n")
    else:
        print("❌ No proposals found.\n")
