import streamlit as st
from utils import get_contract_info
from snapshot import fetch_proposals
from datetime import datetime
from market import get_token_price, get_tvl, get_token_price_history
from volatility import forecast_volatility
from liquidity import get_tvl_history, forecast_tvl
from sentiment import fetch_and_analyze_sentiment
from upgrade_risk import compute_upgrade_risk
import pandas as pd

def format_unix(unix_time):
    try:
        return datetime.utcfromtimestamp(int(unix_time)).strftime('%Y-%m-%d %H:%M UTC')
    except:
        return "N/A"

# 🔧 Streamlit Layout
st.set_page_config(layout="wide")
st.sidebar.title("Settings")

network = st.sidebar.selectbox("Select Network", ["Ethereum", "Polygon", "Arbitrum"])
st.sidebar.caption(f"🔗 Currently selected: `{network}`")

contract_address = st.sidebar.text_input("Enter Smart Contract Address", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

network_spaces = {
    "Ethereum": ["ens.eth", "aavedao.eth", "uniswapgovernance.eth", "rocketpool-dao.eth"],
    "Polygon": ["aavedao.eth", "stgdao.eth", "shapeshiftdao.eth", "aavegotchi.eth"],
    "Arbitrum": ["arbitrumfoundation.eth", "equilibriafi.eth", "stgdao.eth", "shapeshiftdao.eth"]
}
available_spaces = network_spaces.get(network, [])
protocol_space = st.sidebar.selectbox("Select Governance Space", available_spaces)

protocol_config = {
    "aavedao.eth": {"token": "aave", "tvl": "aave"},
    "uniswapgovernance.eth": {"token": "uniswap", "tvl": "uniswap"},
    "rocketpool-dao.eth": {"token": "rocket-pool", "tvl": "rocket-pool"},
    "ens.eth": {"token": "ethereum", "tvl": None},
    "stgdao.eth": {"token": "stargate-finance", "tvl": "stargate"},
    "shapeshiftdao.eth": {"token": "fox-token", "tvl": "shapeshift"},
    "aavegotchi.eth": {"token": "aavegotchi", "tvl": "aavegotchi"},
    "arbitrumfoundation.eth": {"token": "arbitrum", "tvl": "arbitrum"},
    "equilibriafi.eth": {"token": "equilibria", "tvl": "equilibria"},
}
symbol_map = {
    "ethereum": "ETH-USD",
    "aave": "AAVE-USD",
    "uniswap": "UNI-USD",
    "rocket-pool": "RPL-USD",
    "stargate-finance": "STG-USD",
    "fox-token": "FOX-USD",
    "aavegotchi": "GHST-USD",
    "arbitrum": "ARB-USD",
    "equilibria": "EQB-USD"
}

col_left, col_center, col_right = st.columns([1, 2, 1])

with col_left:
    st.header("📡 Network Monitor")
    info = get_contract_info(contract_address)
    if "error" in info:
        st.error(info["error"])
    else:
        st.write(f"🛆 Contract Name: `{info['name']}`")
        st.write(f"📟 Compiler: `{info['compiler']}`")
        st.write("✅ Verified Source" if info['verified'] else "❌ Not Verified")

with col_center:
    st.subheader(f"🗳️ {protocol_space} Governance Proposals")
    proposals = fetch_proposals(protocol_space, limit=15)
    if not proposals:
        st.warning("No proposals found.")
    else:
        for p in proposals:
            st.markdown(f"""
            **🗳️ {p['title']}**
            - State: `{p['state']}`  
            - Start: `{format_unix(p['start'])}`  
            - End: `{format_unix(p['end'])}`
            """)
            st.markdown("---")
        st.caption(f"Showing {len(proposals)} proposals from `{protocol_space}`")

with col_right:
    st.header("🧠 Execution Strategy")
    token_id = protocol_config.get(protocol_space, {}).get("token")
    tvl_id = protocol_config.get(protocol_space, {}).get("tvl")

    token_price = get_token_price(token_id) if token_id else {"price": None, "change_24h": None}
    tvl_data = get_tvl(tvl_id) if tvl_id else {"latest": None, "change": None}

    if token_price["price"]:
        st.metric("💰 Token Price (USD)", f"${token_price['price']:.2f}", f"{token_price['change_24h']:.2f}% 24h")

    if tvl_data["latest"]:
        st.metric("💧 TVL (Total Value Locked)", f"${tvl_data['latest']:.2f}", f"{tvl_data['change']:.2f} USD change")

    if token_price["change_24h"] and abs(token_price["change_24h"]) > 5:
        st.warning("⚠️ High volatility detected. Consider hedging.")
    elif tvl_data["change"] and tvl_data["change"] < -1000000:
        st.warning("⚠️ Liquidity drop detected. Monitor closely.")
    else:
        st.success("✅ Stable market conditions detected.")

    st.markdown("### 📉 30-Day Token Price Trend")
    price_history = get_token_price_history(token_id) if token_id else None
    if isinstance(price_history, pd.DataFrame) and not price_history.empty:
        st.line_chart(price_history.rename(columns={"price": "Token Price (USD)"}))
    else:
        st.info("⚠️ No price history available or failed to fetch data.")

    st.markdown("### 📉 Forecasted Volatility (Next 5 Days)")
    yf_symbol = symbol_map.get(token_id)
    if yf_symbol:
        volatility, err = forecast_volatility(symbol=yf_symbol)
        if err:
            st.info(f"Volatility forecast unavailable: {err}")
        else:
            st.metric("📉 Forecasted Volatility (5-day)", f"{volatility.mean():.2f}%")
    else:
        st.info("📉 Volatility forecast not supported for this token.")

    st.markdown("### 📊 Forecasted TVL (Next 5 Days)")
    tvl_history = get_tvl_history(tvl_id)

    if isinstance(tvl_history, pd.DataFrame) and not tvl_history.empty:
        forecast, err = forecast_tvl(tvl_history)
        if isinstance(forecast, pd.DataFrame) and not forecast.empty:
            chart_data = forecast.rename(columns={"yhat": "Forecasted TVL"}).set_index("ds")
            chart_data.index = pd.to_datetime(chart_data.index)
            st.line_chart(chart_data)
        else:
            st.info(f"TVL forecast unavailable: {err}")
    else:
        st.info("⚠️ No TVL history available to forecast.")

    st.markdown("### 💬 Twitter Sentiment Analysis")
    if token_id:
        with st.spinner("Fetching sentiment..."):
            sentiment, err = fetch_and_analyze_sentiment(query=token_id)
        if err:
            st.info(f"Sentiment unavailable: {err}")
        else:
            st.success(f"👍 Positive: {sentiment['positive']} | 😐 Neutral: {sentiment['neutral']} | 👎 Negative: {sentiment['negative']}")

            st.markdown("### 🔐 Upgrade Risk Score")
            if proposals:
                latest_proposal = proposals[0]
                risk_score, risk_label = compute_upgrade_risk(
                    contract_metadata=info,
                    proposal_data=latest_proposal,
                    sentiment_score=sentiment
                )
                st.metric("🚨 Upgrade Risk Score", f"{risk_score}/100", risk_label)
            else:
                st.info("No recent proposal to evaluate risk.")
    else:
        st.info("⚠️ Token not selected or invalid.")
