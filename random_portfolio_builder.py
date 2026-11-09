import numpy as np
import random
from get_tickers import get_common_ticker_dict

class portfolio_base:
    def __init__(self, tickers: dict = None):
        self.tickers = tickers if tickers is not None else get_common_ticker_dict()

    def select_tickers(self) -> list:
        
        selected_tickers = []
        for c in self.tickers.keys():
            k_value = getattr(self,f"{c}_k", 0)
            if k_value > 0:
                pool = self.tickers.get(c,[])
                actual_k = min(k_value, len(pool))
                if actual_k > 0:
                    selected_tickers.extend(random.sample(pool,k=actual_k))
        return selected_tickers
    
    def build(self, starting_capital: float, prices_dict : dict) -> list[tuple[str, float]]:
        tickers = self.select_tickers()
        if not tickers:
            return []

        weights = np.random.dirichlet(np.ones(len(tickers)) * self.alpha)
        target_allocations = dict(zip(tickers, weights))
        cash = starting_capital
        holdings = []
        for ticker, weight in target_allocations.items():
            price = prices_dict.get(ticker,0)
            if price <= 0:
                continue
            target_dollar_allocation = starting_capital * weight
            shares = target_dollar_allocation // price
            if shares == 0:
                continue
            cash -= shares * price
            holdings.append((ticker, shares))
        if cash < 0:
            raise ValueError("Cash negative after initializing portfolio")
        holdings.append(("CASH-USD", round(cash,2)))

        return holdings
    


class portfolio_conservative(portfolio_base):
    alpha = 3.0
    market_etf_k = 1
    consumer_k = 2
    healthcare_k = 1
    reit_k =1
    telecom_k =1 

class portfolio_moderate(portfolio_base):
    alpha = 1.5
    market_etf_k = 1
    mag7_k = 2
    tech_k = 2
    international_k = 1
    consumer_k = 1 

class portfolio_aggressive(portfolio_base):
    alpha = 1.0
    mag7_k = 3
    tech_k = 3
    crypto_k = 3
    metals_k = 1
    energy_k = 1

class portfolio_crypto(portfolio_base):
    alpha = 0.7
    crypto_k = 3 

