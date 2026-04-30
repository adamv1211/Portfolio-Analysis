import numpy as np
import matplotlib.pyplot as plt
import psycopg
import pandas as pd
from portfolio_data import metrics, dal


def gbm_discrete(conn_str, account_id, N, T, graph=False):
    holdings_df = dal.get_holdings_dat(conn_str, account_id)
    indexed_holdings_df = holdings_df.set_index('ticker')

    log_returns, S_0_array = metrics.log_returns(conn_str, holdings_df['ticker'].tolist())
    cov_matrix = log_returns.cov().values
    mu_array = log_returns.mean().values
    sigma_array = log_returns.std().values
    drift_array = mu_array - (0.5 * sigma_array ** 2)
    corr_matrix = cov_matrix / sigma_array[:,None] / sigma_array
    L = np.linalg.cholesky(corr_matrix)

    Z = np.random.standard_normal((N, T, len(holdings_df['ticker'].tolist())))
    W = Z @ L.T
    daily_log_increments = drift_array + sigma_array * W
    cum_log_increments = np.cumsum(daily_log_increments, axis=1)
    S_0 = S_0_array.values
    paths = S_0 * np.exp(cum_log_increments)
    
    final_prices = paths[:,-1,:]
    weights = indexed_holdings_df['weight'].values
    portfolio_values = paths @ weights

    return portfolio_values


def gbm_closed(conn_str, account_id, N, T, graph=False):
    holdings_df = dal.get_holdings_dat(conn_str, account_id)
    indexed_holdings_df = holdings_df.set_index('ticker')

    log_returns, S_0_array = metrics.log_returns(conn_str, holdings_df['ticker'].tolist())
    
    cov_matrix = log_returns.cov().values
    mu_array = log_returns.mean().values
    sigma_array = log_returns.std().values

    drift_array = (mu_array - (0.5 * sigma_array ** 2)) * T
    vol_array = sigma_array * T ** 0.5

    corr_matrix = cov_matrix / sigma_array[:,None] / sigma_array
    L = np.linalg.cholesky(corr_matrix)

    Z = np.random.standard_normal((N, len(holdings_df['ticker'].tolist())))
    W = Z @ L.T
    
    S_0 = S_0_array.values
  
    final_prices = S_0 * np.exp(drift_array + vol_array * W)
    weights = indexed_holdings_df['weight'].values
    portfolio_values = final_prices @ weights
    print(portfolio_values)
    return portfolio_values
        