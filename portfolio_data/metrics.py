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
     print(E_t / sigma_E * 252 ** 0.5)
     return E_t / sigma_E * 252 ** 0.5

#Not complete
def value_at_risk_parametric(conn_str, account_id, T=252, period='3y'):
     holdings_df = dal.get_holdings_dat(conn_str, account_id)
     indexed_holdings_df = holdings_df.set_index('ticker')
     log_returns_df_wide, R_0_array = log_returns(conn_str, holdings_df["ticker"].tolist())
     
     #Calculations for z score for given confidence interval p
     p = 0.95 
     q = p if p < 0.5 else 1 - p
     t = (-2.0 * np.log(q)) ** 0.5
     # Coeficients found in "Handbook of Mathematical Functions by Abramowitz and Stegun" Formula 26.2.23, pg. 933 (pdf version)
     z = t - ((2.515517 + 0.802853 * t + 0.010328 * t**2) / (1.0 + 1.432788 * t + 0.189269 * t**2 + 0.001308 * t**3))
     if p <= 0.5:
          z = -z
     print(z)
     
     weighted_returns = log_returns_df_wide.dot(indexed_holdings_df['weight'])
     mu = weighted_returns.mean()
     sigma = weighted_returns.std()
     VaR_percent = -1 * (mu * T + z*sigma*np.sqrt(T))
     print(VaR_percent)
     VaR_value = (np.exp(VaR_percent) -1)* indexed_holdings_df['value'].sum()
     print(f"starting: {indexed_holdings_df['value'].sum()} - loss of {VaR_value}. est portfolio value : {(indexed_holdings_df['value'].sum()) + VaR_value}")
     print(VaR_value)


 


