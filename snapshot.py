import requests
from datetime import datetime

# 🧠 Enhanced fetch_proposals to support classifier features

def fetch_proposals(space="aavedao.eth", limit=10):
    url = "https://hub.snapshot.org/graphql"
    headers = {"Content-Type": "application/json"}

    query = {
        "query": """
        query($space: String!, $limit: Int!) {
          proposals(
            first: $limit,
            skip: 0,
            where: { space: $space },
            orderBy: "created",
            orderDirection: desc
          ) {
            id
            title
            state
            start
            end
            scores
            scores_total
            choices
            body
          }
        }
        """,
        "variables": {"space": space, "limit": limit}
    }

    try:
        resp = requests.post(url, json=query, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        proposals = data.get("data", {}).get("proposals") or []

        # Transform structure
        enriched = []
        for p in proposals:
            enriched.append({
                "id": p["id"],
                "title": p["title"],
                "state": p["state"],
                "start": p["start"],
                "end": p["end"],
                "votes_cast": p["scores_total"],
                "voter_count": len(p["scores"]) if p.get("scores") else 0,
                "description": p.get("body") or ""
            })

        print(f"🔁 Snapshot ({space}) response:", enriched)
        return enriched

    except Exception as e:
        print("❌ Snapshot API Error:", e)
        return []
