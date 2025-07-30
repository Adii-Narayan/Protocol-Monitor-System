import re
import numpy as np
from datetime import datetime

def compute_upgrade_risk(contract_metadata, proposal_data, sentiment_score):
        """
        Compute a 0-100 risk score for a protocol upgrade based on multiple factors.
        
        Parameters:
        - contract_metadata: dict with fields like 'compiler', 'source_code', etc.
        - proposal_data: dict with 'start', 'end', 'votes_cast', 'voter_count', 'description'
        - sentiment_score: dict with 'positive', 'neutral', 'negative'

        Returns:
        - (risk_score: float, category: str)
        """
        # --- Feature 1: Code Complexity Heuristic ---
        code_length = len(contract_metadata.get("source_code", ""))
        norm_complexity = min(code_length / 10000, 1.0)

        # --- Feature 2: Proposal Voting Duration ---
        try:
            start_dt = datetime.utcfromtimestamp(int(proposal_data["start"]))
            end_dt = datetime.utcfromtimestamp(int(proposal_data["end"]))
            duration_days = (end_dt - start_dt).total_seconds() / (3600 * 24)
            norm_duration = 1 - min(duration_days / 14.0, 1.0)  # Shorter durations are riskier
        except:
            norm_duration = 0.5  # default medium risk

        # --- Feature 3: Participation Rate ---
        try:
            votes = proposal_data.get("votes_cast", 0)
            voters = proposal_data.get("voter_count", 100)  # assume 100 as fallback
            rate = votes / voters if voters else 0
            norm_participation = 1 - min(rate, 1.0)  # lower participation → higher risk
        except:
            norm_participation = 0.5

        # --- Feature 4: Sentiment Polarity ---
        total = sum(sentiment_score.values())
        negative_ratio = sentiment_score.get("negative", 0) / total if total else 0
        norm_sentiment = min(negative_ratio * 2, 1.0)

        # --- Feature 5: Risky Keywords ---
        keywords = ["upgrade", "critical", "fork", "emergency", "vulnerability", "exploit"]
        description = proposal_data.get("description", "").lower()
        keyword_hits = sum(1 for kw in keywords if kw in description)
        norm_keyword = min(keyword_hits / 3, 1.0)

        # --- Final Weighted Score ---
        weights = [0.25, 0.20, 0.20, 0.20, 0.15]
        features = [norm_complexity, norm_duration, norm_participation, norm_sentiment, norm_keyword]
        score = np.dot(weights, features)

        # --- Risk Category ---
        if score > 0.7:
            label = "🔴 High Risk"
        elif score > 0.4:
            label = "🟠 Medium Risk"
        else:
            label = "🟢 Low Risk"

        return round(score * 100, 2), label
