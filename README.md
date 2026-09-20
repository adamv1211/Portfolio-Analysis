Quantitative Portfolio Risk & Simulation Engine
A high-performance Python framework for brokerage environment simulation and risk modeling.

**Project Status** Features are still being added and worked on as my education in the subject matter increases. The features listed in this Readme are finished.

Overview
This project's goal is to simulate a full-scale brokerage environment. By generating a synthetic population of 1,000 clients and 2,000 diversified accounts(including crypto), the engine provides a robust playground for stress-testing financial models and portfolio strategies.

Core Architecture
The system is built on a Modular ETL Pipeline designed for high scalability and separation of concerns:

Data Acquisition: Automated ingestion of live market data via yfinance.

Storage: PostgreSQL database managed via psycopg3, featuring optimized schema design for time-series price data.

db_setup.py: 
Includes functions for setting up database and seeding tables.

The following functions are for creating and resetting the database. 
db_reset
db_create

The following functions are used to seed the created tables.
seed_customers
seed_accounts
seed_assets
seed_prices

seed_holdings - Adds randomized holdings for accounts.
Accounts are given at least 4 assets from the chosen list of securities added to the assets table.
Crypto assets limited to 0.1 to 3.0
while standard equities are randomized from 1 - 1500

create_table_util.py - A function used  to create new postgres tables.

Models:

gbm.py: Includes discrete and closed-form Geometric Brownian Motion. 

Closed form:

$$V_{\text{portfolio}} = \sum_{i} q_i S_{i,0} \exp\left(\left(\mu_i - \frac{1}{2}\sigma_i^2 \right) T + \sigma_i \sqrt{T} Z_i \right)$$

The discrete function uses a modified version of the closed form function:

$$V^{(n)} = \sum_{i} q_i S_{i, 0} \exp\left(\sum_{k=1}^{T}( \mu_i + \sigma_i W_{i, k}^{(n)})\right)$$


metrics.py: A statistical engine for calculating Sharpe Ratios, Log-Returns, and Value at Risk (VaR).

the following functions are used for arithmatic and logarithmic returns. Currenlty they are not intended to be called alone, and are meant to be used in addition to other functions such as GBM or finding Sharpe ratio. This may change in a later update.

standard_returns(conn_str, tickers)
log_returns(conn_str, tickers)


Sharpe ratio:

$$\text{Sharpe} = \frac{\mathbb{E}[R_p - R_f]}{\sigma_{R_p - R_f}} \sqrt{252}$$

Parametric VaR: 
Returns a dictionary with the following,

VaR_value = traditional VaR output 
VaR_dollar = the corresponsing dollar amount (can be negative)
VaR_percent = the percent lost in a portfolio

For the Z score, I used an approximation found in "Handbook of Mathematical Functions by Abramowitz and Stegun" to avoid importing Scipy for a single use. The formula and constants can be found on pg. 933 (pdf version), figure 26.2.23. 

$$\text{VaR}_{\$} = \left( \exp\left( -\left( \mu_p T + z \sigma_p \sqrt{T} \right) \right) - 1 \right) V_0$$


Data Access Layer (dal.py): Decouples quantitative logic from database queries, ensuring the modeling engine remains database-agnostic.

Contains two functions,
get_holdings_dat - returns a dataframe of a selected account's holdings.

get_tbill_13w - returns a dataframe with the 13 week treasury bill data. Currently only used for Sharpe ratio.



Tech Stack
Core: Python (NumPy, Pandas)

Database: PostgreSQL

Libraries: yfinance, Faker, psycopg3, Matplotlib