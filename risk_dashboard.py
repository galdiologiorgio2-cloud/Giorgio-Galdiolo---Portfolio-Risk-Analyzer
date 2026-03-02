import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from portfolio_risk_analyzer import PortfolioRiskAnalyzer

# Configuration
st.set_page_config(
    page_title="Portfolio Risk Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        font-weight: 600;
    }
    .risk-metric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3498db;
    }
    .safe-metric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #27ae60;
    }
</style>
""", unsafe_allow_html=True)

st.title("Giorgio Galdiolo - Portfolio Risk Analyzer")
st.markdown("*Historical Performance, Risk Metrics & Backtesting*")

# Sidebar Configuration
with st.sidebar:
    st.header("Portfolio Configuration")
    
    # Asset selection
    asset_input = st.text_input(
        "Enter Tickers (comma-separated)",
        value="SPY,IWM,VTV,XLV,XLK,EEM,EFA,BND,GLD,VNQ,USO",
        help="Example: stocks, bonds, commodities"
    )
    
    tickers = [t.strip().upper() for t in asset_input.split(',')]
    
    # Weights
    st.subheader("Asset Weights")
    equal_weight = st.checkbox("Equal Weight", value=False)
    
    if equal_weight:
        weights = np.ones(len(tickers)) / len(tickers)
    else:
        # Default weights for S&P 500 Outperformance Strategy
        default_weights = {
            "SPY": 20, "IWM": 15, "VTV": 10, "XLV": 5, "XLK": 5,
            "EEM": 8, "EFA": 7, "BND": 15, "GLD": 8, "VNQ": 4, "USO": 3
        }
        
        weights = []
        for ticker in tickers:
            default_w = default_weights.get(ticker, int(100/len(tickers)))
            w = st.slider(f"Weight {ticker}", 0, 100, default_w)
            weights.append(w)
        weights = np.array(weights)
    
    # Display weights
    if st.checkbox("Show Weights", value=True):
        weight_df = pd.DataFrame({
            'Ticker': tickers,
            'Weight (%)': (weights / weights.sum()) * 100
        })
        st.dataframe(weight_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Risk parameters
    st.subheader("Risk Parameters")
    confidence_level = st.slider("Confidence Level (VaR)", 0.90, 0.99, 0.95, step=0.01)
    lookback_days = st.slider("Lookback Period (days)", 252, 1260, 756, step=126)  # Default 3 years for stable correlations
    risk_free_rate = st.slider("Risk-Free Rate (annual %)", 0.0, 5.0, 2.0, step=0.1)
    
    st.divider()
    st.subheader("Stress Test Scenarios")
    
    shock_market_crash = st.slider("Market Crash (%)", -50, 0, -20)
    shock_rate_spike = st.slider("Rate Spike (%)", 0, 10, 2)
    shock_vol_spike = st.slider("Volatility Surge (%)", 0, 100, 50)

# Initialize analyzer
try:
    with st.spinner("Loading portfolio data..."):
        analyzer = PortfolioRiskAnalyzer(
            tickers=tickers,
            weights=weights,
            lookback_days=lookback_days,
            rf_rate=risk_free_rate / 100
        )
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Overview",
    "Historical Performance",
    "Risk Metrics",
    "Stress Test",
    "Risk Decomposition",
    "Correlation",
    "Backtesting"
])

with tab1:
    st.subheader("Portfolio Overview")
    
    # Key metrics
    metrics = analyzer.get_portfolio_metrics()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Expected Return",
            f"{metrics['Expected Annual Return']:.2f}%"
        )
    with col2:
        st.metric(
            "Annual Volatility",
            f"{metrics['Annual Volatility (Std)']:.2f}%"
        )
    with col3:
        st.metric(
            "Sharpe Ratio",
            f"{metrics['Sharpe Ratio']:.2f}"
        )
    with col4:
        st.metric(
            "Daily VaR (95%)",
            f"{metrics['Daily VaR (95%)']:.2f}%"
        )
    with col5:
        st.metric(
            "Daily CVaR (95%)",
            f"{metrics['Daily CVaR (95%)']:.2f}%"
        )
    
    # Price chart
    st.subheader("Historical Prices (Normalized)")
    
    normalized_data = analyzer.data / analyzer.data.iloc[0] * 100
    
    fig_prices = go.Figure()
    for ticker in tickers:
        fig_prices.add_trace(go.Scatter(
            x=normalized_data.index,
            y=normalized_data[ticker],
            mode='lines',
            name=ticker,
            line=dict(width=2)
        ))
    
    fig_prices.update_layout(
        title="Normalized Price Performance (Base = 100)",
        xaxis_title="Date",
        yaxis_title="Normalized Price",
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_prices, use_container_width=True)
    
    # Asset weights pie chart
    col1, col2 = st.columns(2)
    
    with col1:
        fig_weights = px.pie(
            values=(weights / weights.sum()) * 100,
            labels=tickers,
            title="Portfolio Allocation"
        )
        st.plotly_chart(fig_weights, use_container_width=True)
    
    with col2:
        st.write("### Asset Allocation Table")
        alloc_df = pd.DataFrame({
            'Asset': tickers,
            'Weight (%)': (weights / weights.sum()) * 100,
            'Current Price': [f"${analyzer.data[t].iloc[-1]:.2f}" for t in tickers]
        })
        st.dataframe(alloc_df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Historical Performance")
    
    # Estrai gli anni disponibili dai dati
    available_years = sorted(analyzer.data.index.year.unique())
    
    col1, col2, col3 = st.columns([1, 1.2, 0.8])
    
    with col1:
        selected_year = st.selectbox("Select Year", available_years, index=len(available_years)-1)
    
    with col2:
        initial_inv = st.slider("Initial Investment (USD)", 1000, 1000000, 100000, step=5000)
    
    with col3:
        st.write("")
        st.write("")
        calculate = st.button("Calculate", use_container_width=True)
    
    if calculate:
            try:
                perf = analyzer.get_historical_performance(year=selected_year, initial_investment=initial_inv)
                
                # Metriche principali
                st.write(f"### Performance in {selected_year}")
                
                col_metric1, col_metric2, col_metric3 = st.columns(3)
                
                with col_metric1:
                    st.metric(
                        "Starting Value",
                        f"$ {perf['start_value']:,.0f}"
                    )
                
                with col_metric2:
                    st.metric(
                        "Ending Value",
                        f"$ {perf['end_value']:,.0f}",
                        f"$ {perf['total_gain_loss']:+,.0f}"
                    )
                
                with col_metric3:
                    st.metric(
                        "Total Return",
                        f"{perf['total_return_pct']:+.2f}%"
                    )
                
                st.divider()
                
                # Equity curve chart - full width
                st.write("### Portfolio Value Over Time")
                
                fig_equity = px.line(
                    perf['equity_curve'],
                    x='date',
                    y='value',
                    title=f'Portfolio Equity Curve ({selected_year})'
                )
                fig_equity.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Portfolio Value (USD)",
                    hovermode='x unified',
                    height=450,
                    template='plotly_white',
                    margin=dict(l=80, r=40, t=50, b=50)
                )
                st.plotly_chart(fig_equity, use_container_width=True)
                
                st.divider()
                
                # Asset performance table - full width
                st.write("### Performance by Asset")
                
                asset_perf_list = []
                for ticker, perf_data in perf['asset_performance'].items():
                    asset_perf_list.append({
                        'Asset': ticker,
                        'Initial': perf_data['initial_value'],
                        'Final': perf_data['final_value'],
                        'Gain/Loss': perf_data['gain_loss'],
                        'Return %': perf_data['return_pct']
                    })
                
                # Crea DataFrame e ordina per return (numerico), poi formatta per visualizzazione
                asset_perf_df = pd.DataFrame(asset_perf_list).sort_values('Return %', ascending=False, key=abs)
                
                # Formatta dopo l'ordinamento
                asset_perf_df_display = asset_perf_df.copy()
                asset_perf_df_display['Initial'] = asset_perf_df_display['Initial'].apply(lambda x: f"$ {x:,.0f}")
                asset_perf_df_display['Final'] = asset_perf_df_display['Final'].apply(lambda x: f"$ {x:,.0f}")
                asset_perf_df_display['Gain/Loss'] = asset_perf_df_display['Gain/Loss'].apply(lambda x: f"$ {x:+,.0f}")
                asset_perf_df_display['Return %'] = asset_perf_df_display['Return %'].apply(lambda x: f"{x:+.2f}%")
                
                st.dataframe(asset_perf_df_display, use_container_width=True, hide_index=True, height=300)
                
                st.divider()
                
                # Best and worst performers
                col_best1, col_best2 = st.columns(2)
                
                best_asset = max(perf['asset_performance'].items(), key=lambda x: x[1]['return_pct'])
                worst_asset = min(perf['asset_performance'].items(), key=lambda x: x[1]['return_pct'])
                
                with col_best1:
                    st.metric(
                        f"Best Performer: {best_asset[0]}",
                        f"{best_asset[1]['return_pct']:+.2f}%",
                        f"$ {best_asset[1]['gain_loss']:+,.0f}"
                    )
                
                with col_best2:
                    st.metric(
                        f"Worst Performer: {worst_asset[0]}",
                        f"{worst_asset[1]['return_pct']:+.2f}%",
                        f"$ {worst_asset[1]['gain_loss']:+,.0f}"
                    )
                
                st.info(f"Trading days in period: {perf['days_traded']}")
                
            except Exception as e:
                st.error(f"Error calculating performance: {str(e)}")

with tab3:
    st.subheader("Risk Metrics & VaR Analysis")
    
    # VAR comparison
    col1, col2, col3 = st.columns(3)
    
    var_hist = analyzer.var_historical(confidence_level)
    var_param = analyzer.var_parametric(confidence_level)
    var_mc = analyzer.var_monte_carlo(confidence_level, simulations=10000)
    
    with col1:
        st.metric(
            "VaR Historical",
            f"{var_hist:.2f}%",
            help="Empirical percentile method"
        )
    with col2:
        st.metric(
            "VaR Parametric",
            f"{var_param:.2f}%",
            help="Normal distribution assumption"
        )
    with col3:
        st.metric(
            "VaR Monte Carlo",
            f"{var_mc:.2f}%",
            help="Simulation-based method"
        )
    
    # CVaR
    cvar = analyzer.cvar_historical(confidence_level)
    
    st.metric(
        f"CVaR (Expected Shortfall) at {confidence_level*100:.0f}% Confidence",
        f"{cvar:.2f}%",
        help="Average loss in worst case scenarios"
    )
    
    # VaR Comparison Chart
    st.subheader("VaR Methodology Comparison")
    
    var_data = pd.DataFrame({
        'Methodology': ['Historical', 'Parametric', 'Monte Carlo'],
        'Daily VaR %': [var_hist, var_param, var_mc]
    })
    
    fig_var = px.bar(
        var_data,
        x='Methodology',
        y='Daily VaR %',
        color='Daily VaR %',
        color_continuous_scale=px.colors.sequential.Reds
    )
    fig_var.update_layout(height=400, template='plotly_white')
    st.plotly_chart(fig_var, use_container_width=True)
    
    # Returns distribution
    st.subheader("Portfolio Returns Distribution")
    
    portfolio_returns = (analyzer.returns @ analyzer.weights) * 100
    
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=portfolio_returns,
        nbinsx=50,
        name='Daily Returns',
        marker_color='#d32f2f'
    ))
    
    # Add VaR line
    fig_hist.add_vline(
        x=-var_hist,
        line_dash="dash",
        line_color="red",
        annotation_text=f"VaR {confidence_level*100:.0f}%",
        annotation_position="top right"
    )
    
    fig_hist.update_layout(
        title="Daily Portfolio Returns Distribution",
        xaxis_title="Return (%)",
        yaxis_title="Frequency",
        height=400,
        template='plotly_white'
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with tab4:
    st.subheader("What If: Market Shocks")
    
    # Stress scenarios
    st.write("### Testing Extreme Scenarios")
    
    shock_scenarios = {
        'Market Crash': shock_market_crash,
        'Rate Spike': shock_rate_spike,
        'Vol Surge': shock_vol_spike
    }
    
    stress_results = analyzer.stress_test(shock_scenarios)
    
    stress_data = []
    for scenario, data in stress_results.items():
        stress_data.append({
            'Scenario': scenario,
            'Portfolio Impact %': data['portfolio_impact']
        })
    
    stress_df = pd.DataFrame(stress_data)
    
    fig_stress = px.bar(
        stress_df,
        x='Scenario',
        y='Portfolio Impact %',
        color='Portfolio Impact %',
        color_continuous_scale=px.colors.diverging.RdYlGn_r
    )
    fig_stress.update_layout(height=400, template='plotly_white')
    st.plotly_chart(fig_stress, use_container_width=True)
    
    # Scenario analysis
    st.divider()
    st.write("### Scenario Analysis - Risk Factor Changes")
    
    scenario_col1, scenario_col2, scenario_col3 = st.columns(3)
    
    with scenario_col1:
        vol_scenario = analyzer.scenario_analysis('volatility_shock')
        with st.expander("Volatility Shock (if vol increases 50%)"):
            st.metric("Current Vol", f"{vol_scenario['current_std']*100:.2f}%")
            st.metric("Shocked Vol", f"{vol_scenario['shocked_std']*100:.2f}%")
            st.metric("Increase", f"{vol_scenario['increase_pct']:.2f}%")
    
    with scenario_col2:
        corr_scenario = analyzer.scenario_analysis('correlation_breakdown')
        with st.expander("Correlation Breakdown (assets move together)"):
            st.metric("Current Vol", f"{corr_scenario['current_std']*100:.2f}%")
            st.metric("Shocked Vol", f"{corr_scenario['shocked_std']*100:.2f}%")
            st.metric("Increase", f"{corr_scenario['increase_pct']:.2f}%")
    
    with scenario_col3:
        regime_scenario = analyzer.scenario_analysis('market_regime_change')
        with st.expander("Market Regime Shift"):
            st.metric("Current Vol", f"{regime_scenario['current_std']*100:.2f}%")
            st.metric("Shocked Vol", f"{regime_scenario['shocked_std']*100:.2f}%")
            st.metric("Increase", f"{regime_scenario['increase_pct']:.2f}%")

with tab5:
    st.subheader("Which Assets Add Risk?")
    
    risk_decomp = analyzer.risk_decomposition()
    
    st.write("### How Much Risk Does Each Asset Contribute")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        fig_contrib = px.pie(
            risk_decomp,
            values='Risk Contribution',
            labels='Asset',
            title='Risk Contribution by Asset'
        )
        st.plotly_chart(fig_contrib, use_container_width=True)
    
    with col2:
        fig_weight = go.Figure()
        fig_weight.add_trace(go.Bar(
            x=risk_decomp['Asset'],
            y=risk_decomp['Weight'],
            name='Weight %',
            marker_color='lightblue'
        ))
        fig_weight.add_trace(go.Bar(
            x=risk_decomp['Asset'],
            y=risk_decomp['Risk Contribution'],
            name='Risk Contribution %',
            marker_color='crimson'
        ))
        fig_weight.update_layout(
            title="Weight vs Risk Contribution",
            barmode='group',
            height=400,
            template='plotly_white'
        )
        st.plotly_chart(fig_weight, use_container_width=True)
    
    st.write("### Risk Decomposition Table")
    st.dataframe(risk_decomp, use_container_width=True, hide_index=True)
    
    # Risk efficiency
    st.write("### Which Assets Are 'Risky' Per Unit")
    st.write("*Higher value = adds more risk for its weight in portfolio*")
    
    risk_efficiency = risk_decomp[['Asset', 'Risk per Unit']].sort_values('Risk per Unit', ascending=False)
    
    fig_efficiency = px.bar(
        risk_efficiency,
        x='Asset',
        y='Risk per Unit',
        color='Risk per Unit',
        color_continuous_scale='Reds'
    )
    fig_efficiency.update_layout(height=400, template='plotly_white')
    st.plotly_chart(fig_efficiency, use_container_width=True)

with tab6:
    st.subheader("How Assets Move Together")
    
    corr_matrix = analyzer.get_correlation_matrix()
    
    # Heatmap
    fig_corr = px.imshow(
        corr_matrix,
        color_continuous_scale='RdBu',
        zmin=-1,
        zmax=1,
        text_auto='.2f',
        aspect='auto',
        title='Asset Correlation Matrix'
    )
    fig_corr.update_layout(height=500)
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Correlation insights
    st.write("### Correlation Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Assets that move together the most:**")
        
        corr_pairs = []
        n = len(corr_matrix)
        for i in range(n):
            for j in range(i+1, n):
                corr_pairs.append({
                    'Pair': f"{corr_matrix.index[i]}-{corr_matrix.columns[j]}",
                    'Correlation': corr_matrix.iloc[i, j]
                })
        
        corr_pairs_df = pd.DataFrame(corr_pairs).sort_values('Correlation', ascending=False)
        st.dataframe(corr_pairs_df.head(5), use_container_width=True, hide_index=True)
    
    with col2:
        st.write("**Assets that move independently (good for diversification):**")
        st.dataframe(corr_pairs_df.tail(5).sort_values('Correlation'), use_container_width=True, hide_index=True)

with tab7:
    st.subheader("VaR Backtesting")
    
    backtest_results = analyzer.backtest_var(confidence_level)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Exception Rate",
            f"{backtest_results['exception_rate']:.2f}%"
        )
    
    with col2:
        st.metric(
            "Expected Rate",
            f"{backtest_results['expected_rate']:.2f}%"
        )
    
    with col3:
        st.metric(
            "Total Exceptions",
            int(backtest_results['total_exceptions'])
        )
    
    with col4:
        model_status = "OK" if backtest_results['model_valid'] else "Check it"
        st.metric("Model Status", model_status)
    
    if backtest_results['model_valid']:
        st.success("The VaR model looks good based on how it performed historically")
    else:
        st.warning("The VaR model had more exceptions than expected. Might need adjusting.")
    
    st.write(f"*Tested {backtest_results['total_days_tested']} days with {confidence_level*100:.0f}% confidence level*")


# Footer
st.divider()
st.markdown("""
---
**Quick Glossary:**
- **VaR**: Worst loss you expect on a bad day (at given confidence level)
- **CVaR**: Average loss when things go even worse than VaR
- **Shocks**: What happens if markets crash, rates spike, volatility spikes
- **Correlation**: How much assets move together (higher = move together more)
- **Backtest**: Testing the model against what actually happened historically
""")
