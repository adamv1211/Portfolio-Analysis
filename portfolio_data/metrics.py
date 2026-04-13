import numpy as np
import pandas as pd
import psycopg



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
                