import psycopg
import pandas as pd

def get_holdings_dat(conn_str, account_id):
    with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                holdings_dat_query = """
                        SELECT holdings.ticker, holdings.shares, prices.close, (holdings.shares * prices.close) AS value,
                        (holdings.shares * prices.close) / SUM(holdings.shares * prices.close) OVER () AS weight,
                        assets.name, assets.asset_type, assets.currency
                        FROM holdings
                        LEFT JOIN(
                            SELECT DISTINCT ON (ticker) ticker, close
                            FROM prices
                            ORDER BY ticker, date DESC
                        )
                        prices ON holdings.ticker = prices.ticker
                        LEFT JOIN assets ON holdings.ticker = assets.ticker
                        WHERE holdings.account_id = %s;
                        """
                cur.execute(holdings_dat_query, (account_id,))
                holdings_dat_df = pd.DataFrame(cur.fetchall(), columns=["ticker", "shares", "close", "value", "weight", "name", "type", "currency"])
                holdings_dat_df[['close', 'value', 'weight']] = holdings_dat_df[['close', 'value', 'weight']].astype(float)
                return holdings_dat_df


def get_tbill_13w(conn_str, period ="3y"):
     pg_period = period.replace("y", " years")
     with psycopg.connect(conn_str) as conn:
          with conn.cursor() as cur:
               tbill_13w_dat_query = """
                            SELECT ticker, date, close
                            FROM prices
                            WHERE ticker = '^IRX' AND date >= CURRENT_DATE - CAST(%s AS INTERVAL);
                            """ 
               cur.execute(tbill_13w_dat_query, (pg_period,))
               tbill_13w_dat_df = pd.DataFrame(cur.fetchall(), columns= ["ticker", "date", "close"])
               tbill_13w_dat_df['close'] = tbill_13w_dat_df["close"].astype(float)
        
               return tbill_13w_dat_df