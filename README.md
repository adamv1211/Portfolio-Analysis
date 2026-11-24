Quantitative Portfolio Risk & Simulation Engine
A high-performance Python framework for brokerage environment simulation and risk modeling.
**FIRST TIME USERS** You need to install PostgreSQL and set yourself as a user before this program will function as intended.

This project was made with PostgreSQL 16.15 on Ubuntu 24.04
1) Install PostgreSQL
**Ubuntu/Debian** `sudo apt update && sudo apt install postgresql`
**Windows** Official PostgreSQL installer from postgresql.org
**macOS** `brew install postgresql@16` or `brew install libpq` or Postgres.app
2) Create a user
In the terminal:
```bash
psql -U postgres -h localhost
```
Then inside psql:

```bash
CREATE USER your_user_name WITH PASSWORD 'your_password';
```
3) Set the admin password
```bash
ALTER USER postgres WITH PASSWORD 'your_admin_password';
```
4) Open the .env.example. Copy this to your .env and change the variables to YOUR username and password.


**Project Status** Features are still being added and worked on as my education in the subject matter increases. The features listed in this Readme are finished.

Overview
This project's goal is to simulate a full-scale brokerage environment. By generating a synthetic population of 1,000 clients and 2,000 diversified accounts(including crypto), the engine provides a robust playground for stress-testing financial models.

Core Architecture
The system is built on a Modular ETL Pipeline designed for high scalability and separation of concerns:

Data Acquisition: Automated ingestion of live market data via yfinance.

Storage: PostgreSQL database managed via psycopg3, featuring optimized schema design for time-series price data.

Models:

Jump_diffusion_discrete

The closed form of Merton's jump diffusion is a popular option pricing model. Since I do not import option prices (yet) I implemented the discrete form to simulate stock price trajectories. Log returns were used so the formula may be slightly different than some textbook variants.

$$\Delta \ln S_{i, t} = \left (\mu_i - \frac{1}{2}\sigma_i^2 \right) \Delta t + \sigma_i \sqrt{\Delta t} W_{i, t} + J_{i, t}$$

In the code, `jump_increments = jump_occurs * jump_sizes` multiplies each jump draw by a Bernoulli jump indicator, so only steps where a jump triggers add a jump return.

Compounding returns
$$\ln S_{i, t} = \ln S_{i, 0} + \sum_{k=1}^{t} \Delta \ln S_{i, k}$$

In the code, `total_log_increments = diffusion_increments + jump_increments` adds each step's diffusive log return and jump log return while `cum_log_increments = np.cumsum(total_log_increments, axis=1)` accumulates those combined log-returns along the time axis for every path and asset at once. 

Asset price level conversion 
$$S_{i, t} = S_{i, 0} \exp(\ln S_{i, t})$$

and finally, new estimated portfolio value
$$V_T = S_T \cdot \text{shares} = \sum_{i=1}^{N} S_{i, T} \times \text{shares}_i$$

gbm.py: Includes discrete and closed-form Geometric Brownian Motion. 

Closed form:
Log returns were used here so ito's Lemma was not needed.
$$V_{\text{portfolio}} = \sum_{i} q_i S_{i,0} \exp\left(\mu_i T + \sigma_i \sqrt{T} Z_i \right)$$

The discrete function uses a modified version of the closed form function:

$$V{(n)} = \sum_{i} q_i S_{i, 0} \exp\left(\sum_{k=1}^{T}( \mu_i + \sigma_i W_{i, k}^{(n)})\right)$$


metrics.py: A statistical engine for calculating Sharpe Ratios, Log-Returns, and Value at Risk (VaR).

The following functions are used for arithmetic and logarithmic returns. Currently they are not intended to be called alone, and are meant to be used in addition to other functions such as GBM or finding Sharpe ratio. This may change in a later update.

standard_returns(conn_str, tickers)


log_returns(conn_str, tickers)

Sortino ratio:

$$\text{Sortino} = \frac{R_p - R_f}{\sqrt{\frac{1}{N} \sum_{t=1}^{N} \min\left(0, \, R_{p,t} - R_{f,\text{daily}}\right)^2} \times \sqrt{A}}$$

Sharpe ratio:

$$\text{Sharpe} = \frac{\mathbb{E}[R_p - R_f]}{\sigma_{R_p - R_f}} \sqrt{252}$$

Parametric VaR: 
Returns a dictionary with the following,

VaR_value = traditional VaR output 
VaR_dollar = the corresponsing dollar amount (can be negative)
VaR_percent = the percent lost in a portfolio

For the Z score, I used an approximation found in "Handbook of Mathematical Functions by Abramowitz and Stegun" to avoid importing Scipy for a single use. The formula and constants can be found on pg. 933 (pdf version), figure 26.2.23. 

$$\text{VaR}= \left( \exp\left( -\left( \mu_p T + z \sigma_p \sqrt{T} \right) \right) - 1 \right) V_0$$


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




Data Access Layer (dal.py): Decouples quantitative logic from database queries, ensuring the modeling engine remains database-agnostic.

Contains two functions,
get_holdings_dat - returns a dataframe of a selected account's holdings.

get_tbill_13w - returns a dataframe with the 13 week treasury bill data. Currently only used for Sharpe ratio.



Tech Stack
Core: Python (NumPy, Pandas)

Database: PostgreSQL

Libraries: yfinance, Faker, psycopg3, Matplotlib