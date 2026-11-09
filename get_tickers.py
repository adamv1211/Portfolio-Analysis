import requests
import numpy as np
import pandas as pd
import random




def get_all_us_tickers():
    url = "https://www.sec.gov/files/company_tickers.json"
    EDGAR_headers ={
        "User-Agent" : "AnalysisSimEngine ProjectAdmin adamv1211@gmail.com"
    }
    try:
        response =  requests.get(url, headers=EDGAR_headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"Successfully loaded {len(data)} entries from EDGAR")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ticker list from EDGAR: {e}")
    
    ticker_df = pd.DataFrame.from_dict(data, orient="index")
    ticker_list = ticker_df["ticker"].str.strip().str.upper().tolist()
    return ticker_list



def get_common_ticker_dict():
    return {
        "market_etf": ("SPY", "VOO", "QQQ", "VTI"),
        "mag7": ("AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"),
        "tech": ("AVGO", "AMD", "ORCL", "CRM", "ADBE", "CSCO", "INTC", "QCOM"),
        "finance": ("JPM", "BAC", "WFC", "C", "GS", "MS", "V", "MA", "AXP", "BLK"),
        "consumer": ("WMT", "COST", "PG", "KO", "PEP", "HD", "NKE", "MCD", "SBUX", "DIS"),
        "healthcare": ("LLY", "JNJ", "UNH", "PFE", "ABBV", "MRK", "TMO", "AMGN"),
        "energy": ("XOM", "CVX", "NEE"),
        "telecom": ("T", "VZ"),
        "industial_and_defense": ("BA", "CAT", "GE", "LMT", "UPS", "HON"),
        "crypto": ("BTC-USD", "ETH-USD", "SOL-USD"),
        "reit": ("VNQ", "O", "AMT"),
        "metals": ("GLD", "SLV"),
        "international": ("VXUS", "EFA")
    }

def get_common_ticker_list(get_common_ticker_dict_func):
    ticker_list = []
    temp = get_common_ticker_dict_func()
    for lst in temp.values():
        ticker_list.extend(lst)
    return ticker_list

