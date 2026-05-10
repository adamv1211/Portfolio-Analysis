import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import psycopg
from faker import Faker
from db_setup import *
from create_table_util import create_table
from models import gbm
from portfolio_data import dal, metrics

         
def main():
    DEBUG = True

    db_name = "portfolio_analysis_sim"
    db_user = os.getenv("DB_USER") 
    db_password = os.getenv("DB_PASS")
    db_admin_password = os.getenv("DB_ADMIN_PASS")

    #psql -h localhost -U postgres -d portfolio_analysis_sim
    conn_str = f"dbname=portfolio_analysis_sim user={db_user} password={db_password} host=localhost"
    admin_conn_str = f"dbname=postgres user=postgres password={db_admin_password} host=localhost"
    tickers = ["AAPL", "NVDA", "TSLA", "MSFT", "SPY", "QQQ", "XLE", "GLD", "BTC-USD", "ETH-USD", "XLF", "PLTR", "JNJ", "AMZN", "XOM", "TLT", "BND", "IWM"]
    tpy = tickers + ["^TNX", "^IRX"]
    tickers.sort()
    period = "10y"

    
    if DEBUG:
        db_reset(db_name, admin_conn_str)
        db_create(db_name, admin_conn_str)
        seed_customers(conn_str)
        seed_accounts(conn_str)
        seed_assets(conn_str, tpy)
        seed_prices(conn_str, tpy, period)
        seed_holdings(conn_str, tickers)
        print("ALL TABLES MADE SUCCESSFULLY")

    #metrics.sharpe(conn_str, 3)
    metrics.value_at_risk_parametric(conn_str, 2,)
    

  
  


if __name__ == "__main__":
    main()
 