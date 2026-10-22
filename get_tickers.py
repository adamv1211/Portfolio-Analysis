import requests
import pandas as pd




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
    print(ticker_df)
    ticker_list = ticker_df["ticker"].str.strip().str.upper().tolist()
    return ticker_list




