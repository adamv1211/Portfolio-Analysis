
import numpy as np
import matplotlib.pyplot as plt
import psycopg
import pandas as pd
from portfolio_data import metrics, holdings_repo


def gbm(conn_str, tickers, N, T):
    log_returns, S_0_array = metrics.log_returns(conn_str, tickers)

    cov_matrix = log_returns.cov().values
    mu_array = log_returns.mean().values
    sigma_array = log_returns.std().values
    drift_array = mu_array - (0.5 * sigma_array ** 2)
    corr_matrix = cov_matrix / sigma_array[:,None] / sigma_array
    L = np.linalg.cholesky(corr_matrix)

    Z = np.random.standard_normal((N, T, len(tickers)))
    W = Z @ L.T
    daily_log_increments = drift_array + sigma_array * W
    cum_log_increments = np.cumsum(daily_log_increments, axis=1)
    S_0 = S_0_array.values
    paths = S_0 * np.exp(cum_log_increments)
    print(paths[:,-1,:])
    return None
        