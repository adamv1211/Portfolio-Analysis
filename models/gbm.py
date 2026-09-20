import numpy as np
import matplotlib.pyplot as plt
import psycopg
import pandas as pd
from portfolio_data import metrics, dal
import sys


full_display = False

if full_display:
    np.set_printoptions(threshold=sys.maxsize, linewidth=200)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)

def gbm_discrete(conn_str, account_id, N, T, graph=False):
    holdings_df = dal.get_holdings_dat(conn_str, account_id)
    indexed_holdings_df = holdings_df.set_index('ticker')

    log_returns, S_0_array = metrics.log_returns(conn_str, holdings_df['ticker'].tolist())
    cov_matrix = log_returns.cov().values
    mu_array = log_returns.mean().values
    sigma_array = log_returns.std().values
    drift_array = mu_array
    corr_matrix = cov_matrix / sigma_array[:,None] / sigma_array
    L = np.linalg.cholesky(corr_matrix)

    Z = np.random.standard_normal((N, T, len(holdings_df['ticker'].tolist())))
    W = Z @ L.T
 
    daily_log_increments = drift_array + sigma_array * W
    cum_log_increments = np.cumsum(daily_log_increments, axis=1)
    S_0 = S_0_array.values
    paths = S_0 * np.exp(cum_log_increments)
    
    final_prices = paths[:,-1,:]
    portfolio_values = final_prices @ (indexed_holdings_df['shares'].values.astype(float))

    

    return portfolio_values


def gbm_closed(conn_str, account_id, N, T, graph=False):
    holdings_df = dal.get_holdings_dat(conn_str, account_id)
    indexed_holdings_df = holdings_df.set_index('ticker')

    log_returns, S_0_array = metrics.log_returns(conn_str, holdings_df['ticker'].tolist())
    
    cov_matrix = log_returns.cov().values
    mu_array = log_returns.mean().values
    sigma_array = log_returns.std().values

    drift_array = mu_array  * T
    vol_array = sigma_array * T ** 0.5

    corr_matrix = cov_matrix / sigma_array[:,None] / sigma_array
    L = np.linalg.cholesky(corr_matrix)

    Z = np.random.standard_normal((N, len(holdings_df['ticker'].tolist())))
    W = Z @ L.T
    
    S_0 = S_0_array.values
  
    final_prices = S_0 * np.exp(drift_array + vol_array * W)
    portfolio_values = final_prices @ (indexed_holdings_df['shares'].values.astype(float))
    

    if graph:
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(12, 8))
      
        count, bins, ignored = plt.hist(portfolio_values, bins=200, density=False, alpha=0.8, color='skyblue', edgecolor='black')
        
        # Add vertical lines for mean and 5% VaR threshold
        mean_val = np.mean(portfolio_values)
        VaR_para = holdings_df["value"].sum() - metrics.value_at_risk_parametric(conn_str, account_id, 0.95, T)["VaR_value"]
        plt.axvline(VaR_para, color='red', linestyle='dashed', linewidth=2, label=f'5% Parametric VaR Threshold: ${VaR_para:,.2f}')
        VaR_empirical = np.percentile(portfolio_values, 5)
        plt.axvline(VaR_empirical, color='orange', linestyle='dashed', linewidth=2, label=f'5% Empirical VaR Threshold: ${VaR_empirical:,.2f}')

        plt.axvline(mean_val, color='green', linestyle='dashed', linewidth=2, label=f'Mean: ${mean_val:,.2f}')
        
        
        plt.title(f'GBM Monte Carlo Simulation: Portfolio Value Distribution, Days={T}, N={N})', fontsize=12, fontweight='bold')
        plt.xlabel('Portfolio Value ($)', fontsize=10)
        plt.ylabel('Density', fontsize=10)
        plt.legend(loc='upper right')
        plt.grid(True, alpha=0.4)
        
        plt.tight_layout()
        plt.show()


    return portfolio_values
        