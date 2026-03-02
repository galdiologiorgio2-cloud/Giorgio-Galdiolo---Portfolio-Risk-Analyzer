# Portfolio Risk Analytics Dashboard

A tool to analyze portfolio risk and understand what could go wrong. Combines VaR, stress testing, and scenario analysis to give you a realistic picture of potential losses.

*By Giorgio Galdiolo*

## Features

### Risk Metrics
- **Value at Risk (VaR)** - 3 methodologies:
  - Historical (Empirical percentile)
  - Parametric (Normal distribution)
  - Monte Carlo (Simulation-based)
- **CVaR / Expected Shortfall** - Tail risk beyond VaR
- **Sharpe Ratio** - Risk-adjusted returns
- **Volatility Analysis** - Portfolio and asset-level

### Stress Testing & Scenarios
- **Predefined Shocks** - Market crash, rate spikes, volatility surge
- **Custom Scenarios** - Test portfolio against personalized market conditions
- **Scenario Analysis** - Volatility shocks, correlation breakdown, regime changes
- **Asset-Level Impact** - See which holdings suffer most

### Advanced Analytics
- **Risk Decomposition** - Identifies which assets contribute most risk
- **Correlation Matrix** - Understand asset relationships
- **VaR Backtesting** - Validates model against historical data
- **Sensitivity Analysis** - How portfolio reacts to individual asset shocks

### Professional Dashboard
- Interactive Streamlit interface
- Real-time data from Yahoo Finance
- Multiple visualization types (charts, tables, heatmaps)
- Customizable portfolio construction
- Adjustable risk parameters

## Installation

### Requirements
- Python 3.8+
- pip or conda

### Setup

1. **Clone or download the project**

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Dashboard

```bash
streamlit run risk_dashboard.py
```

The dashboard will open at `http://localhost:8501`

## User Guide

### 1. Portfolio Configuration (Sidebar)
- **Enter Tickers**: Input asset symbols (e.g., `AAPL,MSFT,JNJ,BND,GLD`)
- **Set Weights**: Use equal weighting or manually specify allocation
- **Risk Parameters**: Choose confidence level, lookback period, risk-free rate

### 2. Dashboard Tabs

#### Overview Tab
- Key portfolio metrics (return, volatility, Sharpe ratio)
- Historical price performance
- Asset allocation visualization

#### Risk Metrics Tab
- Daily VaR at chosen confidence level
- Comparison of 3 VaR methodologies
- CVaR (Expected Shortfall)
- Returns distribution histogram

#### Stress Test Tab
- See how your portfolio reacts to market shocks
- Find which assets hurt the most in bad scenarios
- Test different "what-if" situations

#### Risk Decomposition Tab
- Which assets contribute most to portfolio risk
- Risk contribution vs portfolio weight
- Risk efficiency by asset

#### Correlation Tab
- Full correlation matrix heatmap
- Highest correlations (diversification risk)
- Lowest correlations (diversification benefits)

#### Backtesting Tab
- VaR model validation against history
- Exception rate vs expected rate
- Model quality assessment

## Technical Details

### VaR Methodologies

**Historical VaR**: 
- Uses empirical distribution of past returns
- Most appropriate for non-normal distributions
- No assumptions about return distribution

**Parametric VaR** (Variance-Covariance):
- Assumes normal distribution of returns
- Uses mean and standard deviation
- Faster computation but sensitive to assumptions

**Monte Carlo VaR**:
- Simulates thousands of market scenarios
- Most flexible, handles complex distributions
- Computationally intensive

### What the Numbers Mean

**VaR (Value at Risk)**
The worst you expect to lose on a bad day. If your daily VaR is 2% at 95% confidence, you'd expect a loss of 2% or worse about once every 20 trading days. Pretty useful for knowing your worst case scenarios.

**CVaR (Conditional VaR)**
When things go really wrong (beyond VaR), how bad does it get? This tells you the average loss on those really bad days. More conservative than VaR.

**Sharpe Ratio**
Return you get per unit of risk. Higher is better. Shows if your portfolio actually compensates you for the risk you're taking.

### Backtesting
- Tests how many times realized losses exceeded VaR prediction
- For 95% confidence, should see ~5% exceptions (~13 days per year)
- Validates model calibration

## Project Structure

```
portfolio-risk-dashboard/
├── risk_dashboard.py              # Main Streamlit app
├── portfolio_risk_analyzer.py     # Risk analysis engine
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## What This Teaches

Built with concepts from finance and software engineering:
- VaR calculations and correlation analysis
- How to structure code with classes and modules
- Time series data and statistical analysis
- Making interactive dashboards with Plotly
- Practical risk management techniques

## Customization

### Add Custom Assets
Simply enter different tickers in the sidebar. Works with:
- US Stocks: `AAPL, MSFT, GOOGL, TSLA`
- Bonds: `BND, AGG, TLT`
- Commodities: `GLD, USO, DBC`
- International: `EWJ, EWU, FXI`
- Crypto (some): `BTC-USD, ETH-USD`

### Adjust Risk Parameters
- **Confidence Level**: Higher = more conservative
- **Lookback Period**: Longer = more historical context
- **Risk-Free Rate**: Update to current environment

### Modify Stress Scenarios
Edit sidebar values to test different scenarios.

## Under the Hood

### Portfolio Risk
There's two types: market-wide stuff (interest rates going up) and company-specific stuff (a company has bad news). Diversification helps because different assets don't always move together.

### The Math
Historical VaR looks at what happened before and assumes it could happen again. Stress tests imagine really bad scenarios. In real crises, correlations sometimes break down - things that usually don't move together suddenly do.

### How It Works
The dashboard breaks down which assets contribute most to portfolio risk, shows you the numbers, and lets you test what happens if markets move in different ways.

## Ideas for Later

If you want to expand this:
- Portfolio optimization (find the "best" allocation)
- Volatility modeling that adapts over time
- Factor analysis (what's really driving the risk?)
- Export everything to PDF
- Alerts when risk metrics cross thresholds
- Connect to a real database

## Resources

If you want to understand the theory:
- Markowitz (1952) started all this with portfolio selection
- Jorion's book on Value at Risk is the standard reference
- McNeil et al. on quantitative risk management has solid math


