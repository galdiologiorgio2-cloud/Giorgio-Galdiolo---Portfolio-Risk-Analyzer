# Portfolio Risk Analyzer

**By Giorgio Galdiolo**

An interactive dashboard for comprehensive portfolio risk analysis using modern financial methodologies. Includes VaR calculations, stress testing, scenario analysis, and historical performance tracking with real-time data from Yahoo Finance.

## Features

### Risk Analysis
- **Value at Risk (VaR)** - 3 methodologies:
  - Historical (empirical percentile)
  - Parametric (normal distribution)
  - Monte Carlo (simulation-based, 10k scenarios)
- **CVaR / Expected Shortfall** - Tail risk beyond VaR
- **Sharpe Ratio** - Risk-adjusted return metrics
- **Volatility Analysis** - Portfolio and asset-level

### Stress Testing & Scenarios
- Predefined market shocks (crashes, rate spikes, volatility surges)
- Custom scenario analysis
- Risk decomposition - identifies which holdings contribute most risk
- Correlation matrix analysis with interactive heatmaps

### Historical Performance Tracking
- Analyze portfolio returns by year
- Compare starting vs ending values
- Asset-level performance breakdown
- Best and worst performers identification

### Advanced Analytics
- VaR Backtesting - validates model against historical data
- Risk Decomposition - contributions by asset
- Correlation insights - diversification assessment

## Tech Stack

- **Python 3.8+**
- **Streamlit** - Interactive web dashboard
- **Pandas & NumPy** - Data analysis
- **SciPy** - Statistical calculations
- **Plotly** - Interactive visualizations
- **yfinance** - Real-time market data from Yahoo Finance

## Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Setup

1. Clone the repository
```bash
git clone https://github.com/[your-username]/portfolio-risk-analyzer.git
cd portfolio-risk-analyzer
```

2. Create virtual environment (optional but recommended)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Run the Dashboard
```bash
streamlit run risk_dashboard.py
```

The dashboard will open at `http://localhost:8502`

### Generate HTML Report
```bash
python generate_report.py
```

Generates `risk_report.html` - a standalone interactive report.

## Project Structure

```
portfolio-risk-analyzer/
├── risk_dashboard.py              # Main Streamlit dashboard
├── portfolio_risk_analyzer.py     # Risk calculation engine
├── generate_report.py             # HTML report generator
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore file
└── README.md                      # This file
```

## Dashboard Tabs

1. **Overview** - Portfolio metrics, normalized prices, allocation visualization
2. **Historical Performance** - Year-by-year returns, equity curve, asset performance
3. **Risk Metrics** - VaR comparison, CVaR, returns distribution
4. **Stress Test** - Market shock scenarios, portfolio impact analysis
5. **Risk Decomposition** - Which assets contribute most risk
6. **Correlation** - Asset relationships and diversification benefits
7. **Backtesting** - VaR model validation against historical data

## Data Source

Real-time market data from Yahoo Finance. Supports:
- US Equities (NASDAQ, NYSE)
- ETFs (SPY, IWM, VTV, etc.)
- International funds (EEM, EFA)
- Bonds (BND)
- Commodities (GLD, USO)
- Real Estate (VNQ)

## Mathematical Methodologies

### Historical VaR
Empirical percentile method - uses actual historical returns without distribution assumptions.

### Parametric VaR
Assumes normal distribution using mean and standard deviation. Fast but sensitive to outliers.

### Monte Carlo VaR
Simulates 10,000 portfolio scenarios. Most flexible, handles complex distributions.

### Risk Decomposition
Allocates portfolio risk to individual assets using marginal contribution to risk (MCR).

### Backtesting
Validates VaR model by comparing predicted losses vs actual historical exceptions.

## Known Limitations

- All asset prices in USD (from US market data sources)
- Assumes normal distribution for parametric VaR
- Historical data limited to ~3 years from Yahoo Finance
- Correlation breakdown scenario is simplified model

## Future Enhancements

- Multi-currency support with FX conversion
- GARCH volatility modeling
- Portfolio optimization (Markowitz frontier)
- Real-time alerts
- Monte Carlo with jump-diffusion
- Factor-based risk analysis

## Contact & Support

For questions or suggestions, refer to the code documentation and docstrings.

---

**Disclaimer:** This tool is for educational and analytical purposes. It does not constitute investment advice. Risk analysis models have inherent assumptions and limitations. Always conduct thorough due diligence before investment decisions.
