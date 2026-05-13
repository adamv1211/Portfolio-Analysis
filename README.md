Quantitative Portfolio Risk & Simulation Engine
A high-performance Python framework for brokerage environment simulation and risk modeling.

Overview
This project's goal is to simulate a full-scale brokerage environment. By generating a synthetic population of 1,000 clients and 2,000 diversified accounts(including cyrpto), the engine provides a robust playground for stress-testing financial models and portfolio strategies.

Core Architecture
The system is built on a Modular ETL Pipeline designed for high scalability and separation of concerns:

Data Acquisition: Automated ingestion of live market data via yfinance.

Storage: PostgreSQL database managed via psycopg3, featuring optimized schema design for time-series price data.

Numerical Engine:

gbm.py: Includes discrete and closed-form Geometric Brownian Motion. (Graphs not added yet)

metrics.py: A statistical engine for calculating Sharpe Ratios, Log-Returns, and Value at Risk (VaR).

Data Access Layer (dal.py): Decouples quantitative logic from database queries, ensuring the modeling engine remains database-agnostic.

Current Capabilities & Roadmap
Synthetic Population: Leverages the Faker library to generate realistic client data, mapped to Individual and Retirement (IRA) account structures.

Risk Modeling: Features a vectorized simulation engine for correlated asset paths using Cholesky decomposition.

WIP: Currently implementing the Parametric VaR function

Tech Stack
Core: Python (NumPy, Pandas)

Database: PostgreSQL

Libraries: yfinance, Faker, psycopg3, Matplotlib(not yet implemented)