import os
import requests
from dotenv import load_dotenv

load_dotenv()

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
BASE_URL = "https://api.etherscan.io/api"

def get_contract_info(address):
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": ETHERSCAN_API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    if data["status"] == "1":
        result = data["result"][0]
        print("📦 Contract Name:", result["ContractName"])
        print("🧾 Compiler Version:", result["CompilerVersion"])
        print("📜 Source Code Available:", "Yes" if result["SourceCode"] else "No")
    else:
        print("❌ Error fetching data:", data["result"])

contract_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
get_contract_info(contract_address)
