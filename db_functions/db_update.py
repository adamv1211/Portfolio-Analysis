from datetime import date, timedelta
import psycopg
import yfinance as yf
import pandas as pd



def update_prices(conn_str):
            today = date.today()
            with psycopg.connect(conn_str) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT ticker, MAX(date) as date FROM prices GROUP BY ticker;")
                    most_recent_entries = cur.fetchall() # result is tuple (tickerName, date)
                    for entry in most_recent_entries:
                        if entry[1] < today:
                            print(f"Updating info for {entry[0]}.")
                            ticker_info_download = yf.download(entry[0], start=(entry[1]+timedelta(days=1)), timeout=10)
                            if ticker_info_download is None:
                                 print(f" Could not fetch data for {entry[0]}")
                                 continue
                            df_flat = ticker_info_download.stack(level=1).reset_index()
                            ticker_info_reordered = df_flat[["Ticker", "Date", "Close", "Volume"]]
                            ticker_info_reordered["Date"] = ticker_info_reordered["Date"].dt.strftime("%Y-%m-%d")
                            ticker_info_dict = ticker_info_reordered.to_dict(orient = "records")
                            for row in ticker_info_dict:
                                cur.execute("""
                                        INSERT INTO prices (ticker, date, close, volume)
                                        VALUES (%s, %s, %s, %s)
                                        ON CONFLICT (ticker, date)
                                        DO UPDATE SET
                                        close = EXCLUDED.close,
                                        volume = EXCLUDED.volume

                                    """, (row["Ticker"], row["Date"], row["Close"], row["Volume"],))
                    print(f"All ticker entries up to date.")
                    
