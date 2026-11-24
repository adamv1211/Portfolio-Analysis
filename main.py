import argparse
import os
import yfinance as yf
import psycopg
from db_functions import db_setup, db_update 
from models import gbm, jump_diffusion
from portfolio_data import dal, metrics
from get_tickers import get_all_us_tickers, get_common_ticker_dict,get_common_ticker_list
from cli import *

         
def main():

    force_rebuild = False

    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER") 
    db_password = os.getenv("DB_PASS")
    db_admin_password = os.getenv("DB_ADMIN_PASS")
    edgar_email = os.getenv("EDGAR_EMAIL")
    if not db_user:
        raise ValueError("Missing DB_USER in environment")
    if not db_password:
        raise ValueError("Missing DB_PASS in environment")
    if not db_admin_password:
        raise ValueError("Missing DB_ADMIN_PASS in environment")
    
    conn_str = f"dbname={db_name} user={db_user} password={db_password} host=localhost"
    admin_conn_str = f"dbname=postgres user=postgres password={db_admin_password} host=localhost"

    MASTER_TICKERS_TUPLE = get_all_us_tickers(edgar_email)
    tickers_in_use = []

    common_tickers_list = []
    common_tickers_list = get_common_ticker_list(get_common_ticker_dict)
    tickers_in_use.extend(common_tickers_list)
    
    fixed = ["^TNX", "^IRX"]
    tickers_in_use.extend(fixed)

    tickers_in_use.sort()
    period = "10y"


    if force_rebuild:
        rebuild = True
    else:
        rebuild = db_setup.db_ready_check(conn_str, db_name, tickers_in_use, common_tickers_list, period)

    if not rebuild:
        db_update.update_prices(conn_str)

    else:
        db_setup.db_reset(db_name, admin_conn_str)
        db_setup.db_create(db_name, db_user, admin_conn_str)
        db_setup.seed_customers(conn_str)
        db_setup.seed_accounts(conn_str)
        db_setup.seed_assets(conn_str, tickers_in_use)
        db_setup.seed_prices(conn_str, tickers_in_use, period)
        db_setup.seed_holdings(conn_str, common_tickers_list)
        print("ALL TABLES MADE SUCCESSFULLY")

    account_number = 1
    N=10000 # Number of Sims
    T=252 # T = DAYS (time steps)

    print("Recent prices")
    print(dal.get_recent_prices(conn_str, tickers_in_use))
    print("Holdings")
    print(dal.get_holdings_dat(conn_str, account_number))
    print("13 week tBill")
    print(dal.get_tbill_13w(conn_str))
    print("VaR")
    print(metrics.value_at_risk_parametric(conn_str, account_number))
    print("Sharpe Ratio")
    print(metrics.sharpe(conn_str, account_number))
    print("gbm discrete")
    print(gbm.gbm_discrete(conn_str, account_number, N, T, False))
    print("gbm closed")
    print(gbm.gbm_closed(conn_str, account_number, N, T, False))
    print("Sortino_discrete")
    print(metrics.sortino_discrete(conn_str, account_number))
    print("jump_diffusion_discrete") 
    print(jump_diffusion.jump_diffusion_discrete(conn_str, account_number, N, T))



    #######################################################
    #Currenlty working on adding in cli functionality. I put a pin in this to fix some other issues first
    #######################################################
    # parser = argparse.ArgumentParser(description = "CLI")
    # subparsers = parser.add_subparsers(dest="command", required=True)

    # holdings_parser = subparsers.add_parser("holdings", help="Fetch holdings for an account")
    # holdings_parser.add_argument("account_id", help="account id")
    # holdings_parser.add_argument("--conn_str", default=None, help="Postgres connection string")
    # holdings_parser.add_argument("--cashless", action="store_true", help="Holdings with cash excluded")
    # holdings_parser.set_defaults(func=cmd_get_holdings)
    # args = parser.parse_args()
    # args.func(args)

    

if __name__ == "__main__":
    main()
 