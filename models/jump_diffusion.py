import numpy as np
import pandas as pd
from portfolio_data import metrics, dal
import matplotlib.pyplot as plt

def jump_diffusion_discrete(conn_str, account_id, N, T):
    holdings_df = dal.get_holdings_dat_cashless(conn_str, account_id)
    indexed_holdings_df = holdings_df.set_index("ticker")
    log_returns, S_0_array = metrics.log_returns_cashless(conn_str, holdings_df["ticker"].tolist())
    
    mu_array = log_returns.mean().values
    sigma_array = log_returns.std().values

    drift_array = mu_array -0.5 * (sigma_array ** 2)

    jump_threshold = sigma_array * 3
    jump_filter = np.abs(log_returns - mu_array) > jump_threshold
    jump_intensity = jump_filter.sum() / (len(log_returns) / 252)

    diffusion_df = log_returns.mask(jump_filter)
    diffusion_sigma_daily = diffusion_df.std()

    jump_df = log_returns.where(jump_filter)
    jump_sigma_df = jump_df.std()
    jump_mu_df = jump_df.mean()

    cov_matrix = diffusion_df.cov().values
    corr_matrix = cov_matrix / diffusion_sigma_daily.values[:, None] / diffusion_sigma_daily.values

    num_assets = len(holdings_df["ticker"].tolist())

    L = np.linalg.cholesky(corr_matrix)
    Z = np.random.standard_normal((N, T, num_assets))
    W = Z @ L.T

    diffusion_increments = drift_array + diffusion_sigma_daily.values * W

    jump_occurs = np.random.rand(N, T, num_assets) <= (jump_intensity.values / 252)
    jump_sizes = np.random.normal(jump_mu_df.values, jump_sigma_df.values, size=(N, T, num_assets))
    jump_increments = jump_occurs * jump_sizes

    total_log_increments = diffusion_increments + jump_increments
    cum_log_increments = np.cumsum(total_log_increments, axis=1)

    zeros_shape = (cum_log_increments.shape[0], 1, cum_log_increments.shape[2])
    cum_log_increments_with_t0 = np.concatenate([np.zeros(zeros_shape), cum_log_increments], axis=1)

    S_0 = S_0_array.values
    paths = S_0 * np.exp(cum_log_increments_with_t0)

    final_prices = paths[:, -1, :]
    shares = indexed_holdings_df["shares"].values.astype(float)
    portfolio_values = final_prices @ shares

    
  
    return portfolio_values
    
    
