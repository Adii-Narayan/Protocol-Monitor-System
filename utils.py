# utils.py
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
        return {
            "name": result["ContractName"],
            "compiler": result["CompilerVersion"],
            "verified": True if result["SourceCode"] else False
        }
    else:
        return {"error": data["result"]}
