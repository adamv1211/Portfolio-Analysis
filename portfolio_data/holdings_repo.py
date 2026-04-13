import psycopg
import pandas as pd

def get_holdings_dat(conn_str, account_id):
    with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                holdings_dat_query = """
                        SELECT holdings.ticker, holdings.shares, prices.close, (holdings.shares * prices.close) AS value, assets.name, assets.asset_type, assets.currency
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
                holdings_dat_df = pd.DataFrame(cur.fetchall(), columns=["ticker", "shares", "close", "value", "name", "type", "currency"])
                return holdings_dat_df