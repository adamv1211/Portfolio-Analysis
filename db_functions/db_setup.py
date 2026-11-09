import psycopg
import yfinance as yf
from db_functions.create_table_util import create_table
from faker import Faker
import random
from functools import partial
from random_portfolio_builder import portfolio_base, portfolio_conservative, portfolio_moderate, portfolio_aggressive, portfolio_crypto
from portfolio_data import dal
from get_tickers import get_common_ticker_list

def db_reset(db_name, admin_conn_str):
    with psycopg.connect(admin_conn_str) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS {db_name};")
    print(f"Database {db_name} DROPPED...")


def db_create(db_name, admin_conn_str):
    with psycopg.connect(admin_conn_str) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            try:
                cur.execute(f"CREATE DATABASE {db_name} OWNER adam;")
                print(f"Database {db_name} Added...")
            except psycopg.errors.DuplicateDatabase:
                pass

def db_ready_check(conn_str, db_name, tickers_in_use, common_ticker_list, period):
        rebuild = False
        try:
            with psycopg.connect(conn_str) as conn:
                conn.autocommit = True
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
                    if cur.fetchone():
                        print(f"Database {db_name} found.")
                        expected_tables = ['customers', 'accounts', 'assets', 'prices', 'holdings']
                        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
                        found_tables= [table for (table,) in cur.fetchall()]
                        missing_tables = set(expected_tables) - set(found_tables)
                        if not missing_tables:
                            print("All tables present")
                            return False
                        else:
                            print(f"Tables missing: {missing_tables} ....rebuilding")
                            seed_tasks = {
                                "customers": partial(seed_customers, conn_str),
                                "accounts": partial(seed_accounts, conn_str),
                                "assets": partial(seed_assets, conn_str, tickers_in_use),
                                "prices": partial(seed_prices, conn_str, tickers_in_use, period),
                                "holdings": partial(seed_holdings, conn_str, common_ticker_list)
                            }
                            for table in missing_tables:
                                print(f"Rebuilding table {table}")
                                seed_tasks[table]()
                            print(f"All tables present")    
        except psycopg.OperationalError:
            print(f"Database {db_name} not found.... Rebuilding")
            rebuild = True
        return rebuild


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
            insert_query = """INSERT INTO customers (customer_id, name, ssn, address, phone_number, email)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (customer_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            ssn =  EXCLUDED.ssn,
                            address = EXCLUDED.address,
                            phone_number =  EXCLUDED.phone_number,
                            email =  EXCLUDED.email
                            """
            customer_insert_data = []
            for customer in customers:
                customer_insert_data.append((customer["customer_id"], customer["name"], customer["ssn"], customer["address"], customer["phone_number"], customer["email"]))
            cur.executemany(insert_query, customer_insert_data)


def seed_accounts(conn_str):

    accounts = []
    archetypes = ["conservative", "moderate", "aggressive", "crypto"]
    starting_amounts = [25000.0, 50000.0, 100000.0, 150000.0, 200000.0, 250000.0, 500000.0, 750000.0, 1000000.0, 1500000.0]
    for i in range(1, 1001):
        accounts.append((
            i,
            "Individual Brokerage",
            random.choice(starting_amounts),
            random.choice(archetypes),
        ))

        accounts.append((
            i,
            "Traditional IRA",
            random.choice(starting_amounts),
            random.choice(archetypes),
  
        ))
    
    accounts_schema = {
        "customer_id" : "INT",
        "account_id" : "SERIAL",
        "account_type" : "VARCHAR(30) NOT NULL",
        "starting_capital" : "DECIMAL(12,4)",
        "archetype": "VARCHAR(30) NOT NULL",
    }

    create_table(conn_str, "accounts", accounts_schema, "account_id")
    insert_query = """INSERT INTO accounts (customer_id, account_type, starting_capital, archetype)
                                VALUES (%s, %s, %s, %s)

                                """

    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.executemany(insert_query, accounts)



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
            insert_query = """INSERT INTO assets (ticker, name, asset_type, currency) 
                    VALUES (%s, %s, %s, %s) 
                    ON CONFLICT (ticker) DO UPDATE SET
                    name = EXCLUDED.name,
                    asset_type = EXCLUDED.asset_type,
                    currency = EXCLUDED.currency"""
            asset_insert_data = []
            for asset in asset_info:
                asset_insert_data.append((asset["ticker"], asset["name"], asset["asset_type"], asset["currency"]))
            cur.executemany(insert_query, asset_insert_data)


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
            insert_query = """INSERT INTO prices (ticker, date, close, volume)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (ticker, date) 
                        DO UPDATE SET 
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume
                        """
            prices_insert_data = []
            for asset in prices_info:
                prices_insert_data.append((asset["ticker"], asset["date"], asset["close"], asset["volume"]))
            cur.executemany(insert_query, prices_insert_data)

def seed_holdings(conn_str, common_tickers_list):

    holdings_schema = {
        "account_id": "INT NOT NULL",
        "ticker": "VARCHAR(15) NOT NULL",
        "shares": "DECIMAL(12, 4) NOT NULL",

    }

    archetype_initializers = {
        "conservative" : portfolio_conservative(),
        "moderate" : portfolio_moderate(),
        "aggressive" : portfolio_aggressive(),
        "crypto" : portfolio_crypto(),
    }

 
    prices_dict = dal.get_recent_prices(conn_str, common_tickers_list)

    create_table(conn_str, "holdings", holdings_schema, "account_id, ticker")
    
    holdings_each_account = []
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT account_id, starting_capital, archetype FROM accounts;")
            accounts = cur.fetchall()
            for account_id, starting_capital, archetype in accounts:
                starting_capital = float(starting_capital)
                builder = archetype_initializers.get(archetype)
                if not builder:
                    continue
                holdings = builder.build(starting_capital, prices_dict)
                for ticker, shares in holdings:
                    holdings_each_account.append((account_id, ticker, shares))

            insert_query = """INSERT INTO holdings (account_id, ticker, shares)
                            VALUES (%s, %s, %s) 
                            ON CONFLICT (account_id, ticker) DO UPDATE SET
                            shares = EXCLUDED.shares;
                            """
            cur.executemany(insert_query, holdings_each_account)



