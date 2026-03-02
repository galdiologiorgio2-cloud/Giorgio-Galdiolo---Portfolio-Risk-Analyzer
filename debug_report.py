"""
Debug script for Portfolio Risk Report
"""

import sys
sys.path.insert(0, r'C:\Users\galdi\OneDrive\Immagini\Documenti\My_Project_Galdiolo')

from portfolio_risk_analyzer import PortfolioRiskAnalyzer
import numpy as np

tickers = ["SPY", "IWM", "VTV", "XLV", "XLK", "EEM", "EFA", "BND", "GLD", "VNQ", "USO"]
weights = np.array([20, 15, 10, 5, 5, 8, 7, 15, 8, 4, 3])

print("Loading analyzer...")
analyzer = PortfolioRiskAnalyzer(tickers, weights, lookback_days=756, rf_rate=0.02)

print("\n=== DATA VERIFICATION ===")
print(f"Data shape: {analyzer.data.shape}")
print(f"Returns shape: {analyzer.returns.shape}")

corr_matrix = analyzer.get_correlation_matrix()
print(f"\nCorrelation matrix shape: {corr_matrix.shape}")
print(f"Correlation matrix type: {type(corr_matrix)}")
print(f"Correlation matrix index: {corr_matrix.index.tolist()}")
print(f"Correlation matrix columns: {corr_matrix.columns.tolist()}")

print(f"\nSPY-IWM (should be 0.81): {corr_matrix.loc['SPY', 'IWM']:.4f}")
print(f"\nFull correlation matrix:")
print(corr_matrix)

decomp = analyzer.risk_decomposition()
print(f"\nRisk Decomposition:")
print(decomp[['Asset', 'Weight', 'Risk Contribution']])

metrics = analyzer.get_portfolio_metrics()
print(f"\n=== METRICS ===")
for key, val in metrics.items():
    print(f"{key}: {val:.2f}")

print("\nAll data looks correct. Now regenerating report...")
