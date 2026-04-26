import numpy as np
import pandas as pd
import psycopg
from portfolio_data import dal

def standard_returns(conn_str, tickers):
     with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                ticker_dat_query = """
                        SELECT ticker, date, close
                        FROM prices
                        WHERE ticker = ANY(%s) AND date >= CURRENT_DATE - INTERVAL '3 years'
                        ORDER BY date ASC, ticker ASC;
                        """
                cur.execute(ticker_dat_query, (tickers,))                 
                ticker_dat_df = pd.DataFrame(cur.fetchall(), columns = [ "ticker", "date", "close"])

                ticker_dat_df["close"] = ticker_dat_df["close"].astype(float)

                ticker_dat_df["date"] = pd.to_datetime(ticker_dat_df["date"])
                ticker_dat_df_wide = ticker_dat_df.pivot(index="date", columns="ticker", values="close")

                existing_tickers = [t for t in tickers if t in ticker_dat_df_wide.columns]
                ticker_dat_df_wide = ticker_dat_df_wide[existing_tickers]
                
                ticker_dat_df_wide = ticker_dat_df_wide.ffill()
                business_calendar = pd.bdate_range(start= ticker_dat_df_wide.index.min(), end= ticker_dat_df_wide.index.max())
                ticker_dat_df_wide = ticker_dat_df_wide.reindex(business_calendar)
                return ticker_dat_df_wide.pct_change().dropna(how="all"), ticker_dat_df_wide.iloc[-1]


def log_returns(conn_str, tickers):
    with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                ticker_dat_query = """
                        SELECT ticker, date, close
                        FROM prices
                        WHERE ticker = ANY(%s) AND date >= CURRENT_DATE - INTERVAL '3 years'
                        ORDER BY date ASC, ticker ASC;
                        """
                cur.execute(ticker_dat_query, (tickers,))                 
                ticker_dat_df = pd.DataFrame(cur.fetchall(), columns = [ "ticker", "date", "close"])

                ticker_dat_df["close"] = ticker_dat_df["close"].astype(float)

                ticker_dat_df["date"] = pd.to_datetime(ticker_dat_df["date"])
                ticker_dat_df_wide = ticker_dat_df.pivot(index="date", columns="ticker", values="close")

                existing_tickers = [t for t in tickers if t in ticker_dat_df_wide.columns]
                ticker_dat_df_wide = ticker_dat_df_wide[existing_tickers]
                
                ticker_dat_df_wide = ticker_dat_df_wide.ffill()
                business_calendar = pd.bdate_range(start= ticker_dat_df_wide.index.min(), end= ticker_dat_df_wide.index.max())
                ticker_dat_df_wide = ticker_dat_df_wide.reindex(business_calendar)

                return np.log(ticker_dat_df_wide / ticker_dat_df_wide.shift(1)).dropna(how="all"), ticker_dat_df_wide.iloc[-1]
                


def sharpe(conn_str, account_id, period='3y'):
     holdings_df = dal.get_holdings_dat(conn_str, account_id)
     indexed_holdings_df = holdings_df.set_index('ticker')
     
     standard_returns_df_wide, R_0_array = standard_returns(conn_str, holdings_df["ticker"].tolist())

     tbill_13w_dat_df = dal.get_tbill_13w(conn_str, period)
     tbill_13w_dat_df['date'] = pd.to_datetime(tbill_13w_dat_df['date'])
     tbill_13w_dat_df = tbill_13w_dat_df.set_index('date')
     tbill_13w_dat_df = tbill_13w_dat_df.drop(columns=['ticker'])
     
     R_f_daily_df = (1 + (tbill_13w_dat_df['close']/100)) ** (1/252) -1

     weighted_returns = standard_returns_df_wide.dot(indexed_holdings_df['weight'])
    
     excess_returns = weighted_returns.subtract(R_f_daily_df, axis=0)
     excess_returns = excess_returns.dropna()

     E_t = excess_returns.mean()
     sigma_E = excess_returns.std()
     
     return E_t / sigma_E * 252 ** 0.5




 


