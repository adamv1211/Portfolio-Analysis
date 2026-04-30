import psycopg
import yfinance as yf
from create_table_util import create_table
from faker import Faker
import random


def db_reset(db_name, admin_conn_str = "dbname=postgres user=postgres password=LUNA host=localhost"):
    with psycopg.connect(admin_conn_str) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS {db_name};")


def db_create(db_name, admin_conn_str = "dbname=postgres user=postgres password=LUNA host=localhost"):
    with psycopg.connect(admin_conn_str) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            try:
                cur.execute(f"CREATE DATABASE {db_name} OWNER adam;")
            except psycopg.errors.DuplicateDatabase:
                pass



def seed_customers(conn_str):
    Faker.seed(2401)
    fake = Faker()
    
    customers = []
    for i in range(1000):
        customers.append({
            "customer_id": i + 1,
            "name": fake.name(),
            "ssn": fake.ssn(),
            "address": fake.address().replace("\n",", "),
            "phone_number": fake.phone_number(),
            "email": fake.email()

        })
    
    customers_schema = {
        "customer_id" : "INT",
        "name" : "VARCHAR(100) NOT NULL",
        "ssn": "VARCHAR(30) NOT NULL",
        "address": "TEXT NOT NULL",
        "phone_number": "VARCHAR(30) NOT NULL",
        "email": "VARCHAR(255)",

    }



    create_table(conn_str, "customers", customers_schema, "customer_id")
    
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            for customer in customers:
                cur.execute("""INSERT INTO customers (customer_id, name, ssn, address, phone_number, email)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (customer_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            ssn =  EXCLUDED.ssn,
                            address = EXCLUDED.address,
                            phone_number =  EXCLUDED.phone_number,
                            email =  EXCLUDED.email
                            """, (customer["customer_id"], customer["name"], customer["ssn"], customer["address"], customer["phone_number"], customer["email"])
                )


def seed_accounts(conn_str):

    accounts = []
    for i in range(1, 1001):
        accounts.append({
            "customer_id": i,
            "account_type": "Individual Brokerage",
    
        })

        accounts.append({
            "customer_id": i,
            "account_type": "Traditional IRA",
  
        })
    
    accounts_schema = {
        "customer_id" : "INT",
        "account_id" : "SERIAL",
        "account_type" : "VARCHAR(30) NOT NULL",
    }

    create_table(conn_str, "accounts", accounts_schema, "account_id")

    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            for account in accounts:
                cur.execute("""INSERT INTO accounts (customer_id, account_type)
                                VALUES (%s, %s)
                                ON CONFLICT (account_id) DO UPDATE SET
                                customer_id = EXCLUDED.customer_id,
                                account_type = EXCLUDED.account_type
                                """, (account["customer_id"], account["account_type"])
                )


def seed_assets(conn_str, tickers):
    asset_info = []
    for i in tickers:
        tikr = yf.Ticker(i)
        info = tikr.info
        asset_info.append({
            "ticker" : i,
            "name" : info.get("longName", i),
            "asset_type" : info.get("quoteType", "unknown"),
            "currency" : info.get("currency", "USD")
        })
    assets_schema = {
        "ticker" : "VARCHAR(10) NOT NULL",
        "name" : "VARCHAR(100)",
        "asset_type" : "VARCHAR(50)",
        "currency" : "VARCHAR(10)"
    }

    create_table(conn_str, "assets", assets_schema,"ticker")

    
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            for asset in asset_info:
                cur.execute("""INSERT INTO assets (ticker, name, asset_type, currency) 
                    VALUES (%s, %s, %s, %s) 
                    ON CONFLICT (ticker) DO UPDATE SET
                    name = EXCLUDED.name,
                    asset_type = EXCLUDED.asset_type,
                    currency = EXCLUDED.currency""", (asset["ticker"], asset["name"], asset["asset_type"], asset["currency"]))

def seed_prices(conn_str, tickers, period ="3y"):
    prices_info = []
    for i in tickers:
        tikr = yf.Ticker(i)
        price_hist = tikr.history(period)
        for date, r in price_hist.iterrows():   
            prices_info.append({
                "ticker" : i,
                "date" : date.strftime("%Y-%m-%d"),
                "close" : r["Close"],
                "volume" : r["Volume"]
            
        })
    prices_schema = {
        "ticker" : "VARCHAR(10) NOT NULL",
        "date" : "DATE NOT NULL",
        "close" : "DECIMAL(12,4) NOT NULL",
        "volume" : "BIGINT"
    }
    create_table(conn_str, "prices", prices_schema, "ticker, date")
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            for asset in prices_info:
                cur.execute("""INSERT INTO prices (ticker, date, close, volume)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (ticker, date) 
                        DO UPDATE SET 
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume
                        """, (asset["ticker"], asset["date"], asset["close"], asset["volume"]))
def seed_holdings(conn_str, tickers):

    holdings_schema = {
        "account_id": "INT NOT NULL",
        "ticker": "VARCHAR(15) NOT NULL",
        "shares": "DECIMAL(12, 4) NOT NULL",

    }
    create_table(conn_str, "holdings", holdings_schema, "account_id, ticker")
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT account_id FROM accounts")
            accounts = [row[0] for row in cur.fetchall()]

            for account_id in accounts:
                owned = random.sample(tickers, k=random.randint(1, 16))
                for ticker in owned:
                    shares = random.randint(1, 1204)
                    cur.execute("""INSERT INTO holdings (account_id, ticker, shares)
                                    VALUES (%s, %s, %s)
                                    ON CONFLICT (account_id, ticker) DO UPDATE SET
                                    shares = EXCLUDED.shares
                                """, (account_id, ticker, shares)
                                )