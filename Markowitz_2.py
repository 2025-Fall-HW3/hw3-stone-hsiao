"""
Package Import
"""
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import quantstats as qs
import gurobipy as gp
import warnings
import argparse
import sys

"""
Project Setup
"""
warnings.simplefilter(action="ignore", category=FutureWarning)

assets = [
    "SPY",
    "XLB",
    "XLC",
    "XLE",
    "XLF",
    "XLI",
    "XLK",
    "XLP",
    "XLRE",
    "XLU",
    "XLV",
    "XLY",
]

# Initialize Bdf and df
Bdf = pd.DataFrame()
for asset in assets:
    raw = yf.download(asset, start="2012-01-01", end="2024-04-01", auto_adjust = False)
    Bdf[asset] = raw['Adj Close']

df = Bdf.loc["2019-01-01":"2024-04-01"]

"""
Strategy Creation

Create your own strategy, you can add parameter but please remain "price" and "exclude" unchanged
"""


class MyPortfolio:
    """
    NOTE: You can modify the initialization function
    """

    def __init__(self, price, exclude, lookback=50, gamma=0):
        self.price = price
        self.returns = price.pct_change().fillna(0)
        self.exclude = exclude
        self.lookback = lookback
        self.gamma = gamma

    def calculate_weights(self):
        # Get the assets by excluding the specified column
        assets = self.price.columns[self.price.columns != self.exclude]

        # Calculate the portfolio weights
        self.portfolio_weights = pd.DataFrame(
            index=self.price.index, columns=self.price.columns
        )

        """
        TODO: Complete Task 4 Below
        """
        
        # Strategy design (momentum + inverse-volatility among top k):
        # 1) Compute momentum over lookback days (total return)
        # 2) Choose top k sectors by momentum (k = 3)
        # 3) Within chosen sectors, assign weights proportional to inverse volatility
        # (so lower vol sectors get more weight)
        # 4) If all momenta are negative, fall back to equal weight across all sectors


        k = 3
        eps = 1e-8
        for i in range(self.lookback, len(self.price)):
            date = self.price.index[i]
            window = self.price.iloc[i - self.lookback : i]
            # compute momentum as (last / first) - 1 over window
            momentum = window.iloc[-1] / window.iloc[0] - 1.0
            # select assets excluding the benchmark
            mom = momentum[assets]


            # pick top k by momentum
            topk = mom.sort_values(ascending=False).iloc[:k]
            if topk.isnull().all():
                # fallback: equal weight
                w = pd.Series(0.0, index=assets)
                w[:] = 1.0 / len(assets)
            else:
                # if all topk <= 0, still pick those with highest (less negative)
                selected = topk.index.tolist()
                # compute inverse vol over the same window
                vol = window[assets].pct_change().dropna().std()
                inv_vol = 1.0 / (vol + eps)
                inv_vol_sel = inv_vol.loc[selected]
                if inv_vol_sel.sum() == 0:
                    weights_sel = np.repeat(1.0 / len(selected), len(selected))
                else:
                    weights_sel = inv_vol_sel / inv_vol_sel.sum()
                # assign to full vector
                w = pd.Series(0.0, index=assets)
                for idx, wt in zip(selected, weights_sel):
                    w.loc[idx] = wt


            # Set weights for that date
            self.portfolio_weights.loc[date, assets] = w.values
            # Ensure exclude column is zero
            self.portfolio_weights.loc[date, self.exclude] = 0.0

        """
        TODO: Complete Task 4 Above
        """

        self.portfolio_weights.ffill(inplace=True)
        self.portfolio_weights.fillna(0, inplace=True)

    def calculate_portfolio_returns(self):
        # Ensure weights are calculated
        if not hasattr(self, "portfolio_weights"):
            self.calculate_weights()

        # Calculate the portfolio returns
        self.portfolio_returns = self.returns.copy()
        assets = self.price.columns[self.price.columns != self.exclude]
        self.portfolio_returns["Portfolio"] = (
            self.portfolio_returns[assets]
            .mul(self.portfolio_weights[assets])
            .sum(axis=1)
        )

    def get_results(self):
        # Ensure portfolio returns are calculated
        if not hasattr(self, "portfolio_returns"):
            self.calculate_portfolio_returns()

        return self.portfolio_weights, self.portfolio_returns


if __name__ == "__main__":
    # Import grading system (protected file in GitHub Classroom)
    from grader_2 import AssignmentJudge
    
    parser = argparse.ArgumentParser(
        description="Introduction to Fintech Assignment 3 Part 12"
    )

    parser.add_argument(
        "--score",
        action="append",
        help="Score for assignment",
    )

    parser.add_argument(
        "--allocation",
        action="append",
        help="Allocation for asset",
    )

    parser.add_argument(
        "--performance",
        action="append",
        help="Performance for portfolio",
    )

    parser.add_argument(
        "--report", action="append", help="Report for evaluation metric"
    )

    parser.add_argument(
        "--cumulative", action="append", help="Cumulative product result"
    )

    args = parser.parse_args()

    judge = AssignmentJudge()
    
    # All grading logic is protected in grader_2.py
    judge.run_grading(args)
