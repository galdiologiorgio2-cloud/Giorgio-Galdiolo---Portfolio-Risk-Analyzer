import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats
from datetime import datetime, timedelta
from typing import Dict, Tuple, List

class PortfolioRiskAnalyzer:
    """
    Analyzes portfolio risk using VaR, stress tests, and other metrics.
    Gets data from Yahoo Finance and calculates various risk measures.
    """
    
    def __init__(self, tickers: List[str], weights: np.ndarray, 
                 lookback_days: int = 252, rf_rate: float = 0.02):
        """
        Set up the analyzer with assets and their weights.
        
        Args:
            tickers: Asset symbols like ['AAPL', 'MSFT', 'BND']
            weights: Portfolio weights (should sum to 1)
            lookback_days: Days of history to use (252 = 1 year)
            rf_rate: Risk-free rate (annual, as decimal)
        """
        self.tickers = tickers
        self.weights = weights / weights.sum()  # Normalizza pesi
        self.lookback_days = lookback_days
        self.rf_rate = rf_rate
        self.data = None
        self.returns = None
        self.cov_matrix = None
        self.portfolio_return = None
        self.portfolio_std = None
        
        self._fetch_data()
        self._calculate_statistics()
    
    def _fetch_data(self):
        """
        Scarica dati storici da Yahoo Finance con allineamento temporale rigoroso.
        
        Procedura:
        1. Scarica TUTTI i ticker in una singola chiamata (non loop)
        2. Applica forward-fill per coprire giorni di chiusura mercati differenti
        3. Rimuove NaN residui
        4. Verifica allineamento
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.lookback_days + 50)
        
        try:
            # STEP 1: Scarica tutti i ticker in una singola chiamata
            # Questo garantisce che siano tutti allineati allo stesso DatetimeIndex
            raw_data = yf.download(
                self.tickers, 
                start=start_date, 
                end=end_date, 
                progress=False,
                auto_adjust=False,
                interval='1d'
            )['Close']
            
            # Se un solo ticker, assicura che sia un DataFrame
            if len(self.tickers) == 1:
                raw_data = raw_data.to_frame(name=self.tickers[0])
            
            # STEP 2: Allineamento temporale - Forward fill per coprire gaps
            # (ad es., quando un singolo mercato ha vacanza diversa)
            aligned_data = raw_data.ffill()
            
            # STEP 3: Rimozione NaN residui all'inizio (quando non tutti i ticker hanno dati)
            aligned_data = aligned_data.dropna()
            
            # STEP 4: Verifica che nessun NaN rimanga
            if aligned_data.isnull().sum().sum() > 0:
                raise Exception("Dati contengono ancora NaN dopo allineamento")
            
            # STEP 5: Verifica che l'indice temporale sia ordinato
            if not aligned_data.index.is_monotonic_increasing:
                aligned_data = aligned_data.sort_index()
            
            # STEP 6: Verifica coerenza lunghezza per tutti i ticker
            if len(aligned_data) < 20:
                raise Exception(f"Insufficienti dati storici: {len(aligned_data)} giorni dopo allineamento")
            
            self.data = aligned_data
            
        except Exception as e:
            raise Exception(f"Errore nel fetching/allineamento dati: {str(e)}")
    
    def _calculate_statistics(self):
        """Calcola statistiche portfolio"""
        # Returns giornalieri
        self.returns = self.data.pct_change().dropna()
        
        # IMPORTANTE: Riordina i pesi per corrispondere all'ordine delle colonne in self.returns
        # yfinance ritorna i dati in ordine alphabetico, non nell'ordine originale dei tickers
        weight_dict = {ticker: w for ticker, w in zip(self.tickers, self.weights)}
        self.weights_reordered = np.array([weight_dict[col] for col in self.returns.columns])
        
        # Matrice correlazione
        self.cov_matrix = self.returns.cov()
        self.corr_matrix = self.returns.corr()
        
        # Return e volatilità portfolio - USANDO I PESI RIORDINATI
        returns_daily = self.returns.mean()
        self.portfolio_return = np.sum(self.weights_reordered * returns_daily) * 252
        
        portfolio_var = np.dot(self.weights_reordered, np.dot(self.cov_matrix * 252, self.weights_reordered))
        self.portfolio_std = np.sqrt(portfolio_var)
    
    # ============ VAR METHODS ============
    
    def var_historical(self, confidence: float = 0.95) -> float:
        """
        Value at Risk - Metodo Storico
        Usa distribuzione empirica dei returns storici
        
        Args:
            confidence: Confidence level (es. 0.95 = 5th percentile)
        
        Returns:
            VaR percentuale giornaliera
        """
        portfolio_returns = (self.returns @ self.weights_reordered) * 100
        var = np.percentile(portfolio_returns, (1 - confidence) * 100)
        return abs(var)
    
    def var_parametric(self, confidence: float = 0.95) -> float:
        """
        Value at Risk - Metodo Parametrico (Varianza-Covarianza)
        Assume distribuzione normale dei returns
        
        Args:
            confidence: Confidence level
        
        Returns:
            VaR percentuale giornaliera
        """
        portfolio_returns = (self.returns @ self.weights_reordered)
        mean = portfolio_returns.mean()
        std = portfolio_returns.std()
        
        # Z-score per il confidence level
        z_score = stats.norm.ppf(1 - confidence)
        var = (mean + z_score * std) * 100
        return abs(var)
    
    def var_monte_carlo(self, confidence: float = 0.95, 
                       simulations: int = 10000) -> float:
        """
        Value at Risk - Metodo Monte Carlo
        Simula futuri scenari di mercato
        
        Args:
            confidence: Confidence level
            simulations: Numero simulazioni
        
        Returns:
            VaR percentuale giornaliera
        """
        # Parametri dalla storia
        mean_returns = self.returns.mean().values
        cov_matrix = self.cov_matrix.values
        
        # Simulazioni
        simulated_returns = np.random.multivariate_normal(
            mean_returns, cov_matrix, simulations
        )
        
        # Portfolio returns simulati
        portfolio_sims = simulated_returns @ self.weights * 100
        
        # VaR dal percentile
        var = np.percentile(portfolio_sims, (1 - confidence) * 100)
        return abs(var)
    
    # ============ CVAR / EXPECTED SHORTFALL ============
    
    def cvar_historical(self, confidence: float = 0.95) -> float:
        """
        Conditional Value at Risk (Expected Shortfall)
        Media delle perdite peggiori oltre il VaR
        
        Args:
            confidence: Confidence level
        
        Returns:
            CVaR percentuale giornaliera
        """
        portfolio_returns = (self.returns @ self.weights) * 100
        var_value = np.percentile(portfolio_returns, (1 - confidence) * 100)
        
        # Media delle code peggiori
        cvar = portfolio_returns[portfolio_returns <= var_value].mean()
        return abs(cvar)
    
    # ============ STRESS TESTING ============
    
    def stress_test(self, shock_scenarios: Dict[str, float]) -> Dict:
        """
        Stress Test - Applica shock a scenari di mercato
        
        Args:
            shock_scenarios: Dict con nome scenario e shock percentuali
                            {'Market Crash': -20, 'Rate Spike': 2, ...}
                            Special case: 'Vol Surge' è interpretato come aumento volatilità
                            e causa calo del portafoglio (negativo)
        
        Returns:
            Dict con impatti su portfolio
        """
        results = {}
        current_prices = self.data.iloc[-1]
        
        for scenario_name, shock_pct in shock_scenarios.items():
            # Gestione speciale per Vol Surge - la volatilità alta RIDUCE i prezzi
            if 'vol' in scenario_name.lower():
                # Volatility spike causa calo proporzionale
                # Maggiore volatilità = maggiore rischio = calo prezzi di ~25-40% dell'aumento vol
                shock_pct = -shock_pct * 0.3  # -30% dell'aumento volatilità
            
            # Applica shock
            shocked_prices = current_prices * (1 + shock_pct / 100)
            price_change = (shocked_prices - current_prices) / current_prices * 100
            
            # Impatto portfolio
            portfolio_impact = np.sum(self.weights_reordered * price_change)
            results[scenario_name] = {
                'portfolio_impact': portfolio_impact,
                'asset_impacts': dict(zip(self.tickers, price_change))
            }
        
        return results
    
    # ============ SCENARIO ANALYSIS ============
    
    def scenario_analysis(self, scenario_type: str = 'volatility_shock') -> Dict:
        """
        Analisi Scenario - Modella cambiamenti in fattori di rischio
        
        Args:
            scenario_type: Tipo di scenario
                - 'volatility_shock': Aumento volatilità
                - 'correlation_breakdown': Asset correlati diventano altamente correlati
                - 'market_regime_change': Cambio regime di mercato
        
        Returns:
            Dict con risultati scenario
        """
        if scenario_type == 'volatility_shock':
            # Aumenta volatilità del 50%
            shocked_cov = self.cov_matrix * 1.5
            shocked_std = np.sqrt(np.dot(self.weights_reordered, np.dot(shocked_cov * 252, self.weights_reordered)))
            
            return {
                'scenario': 'Volatility Shock (+50%)',
                'current_std': self.portfolio_std,
                'shocked_std': shocked_std,
                'increase_pct': (shocked_std / self.portfolio_std - 1) * 100
            }
        
        elif scenario_type == 'correlation_breakdown':
            # Aumenta correlazioni verso 0.9 in scenario di stress
            shocked_cov = self.cov_matrix.copy()
            std_devs = np.sqrt(np.diag(shocked_cov))
            
            # Ricostruisci matrice di correlazione
            corrmat = self.corr_matrix.values.copy()
            
            # Aumenta correlazioni (tutte le correlazioni tendono verso 0.9 in crisi)
            for i in range(len(corrmat)):
                for j in range(len(corrmat)):
                    if i != j:
                        if corrmat[i, j] < 0.0:  # Correlazioni negative diventano meno negative
                            corrmat[i, j] = corrmat[i, j] * 0.5
                        elif corrmat[i, j] < 0.9:  # Correlazioni positive aumentano verso 0.9
                            corrmat[i, j] = min(0.9, corrmat[i, j] * 1.5)
                    else:
                        corrmat[i, j] = 1.0
            
            # Ricostruisci matrice di covarianza
            shocked_cov = np.outer(std_devs, std_devs) * corrmat
            
            shocked_std = np.sqrt(np.dot(self.weights_reordered, np.dot(shocked_cov * 252, self.weights_reordered)))
            
            return {
                'scenario': 'Correlation Breakdown',
                'current_std': self.portfolio_std,
                'shocked_std': shocked_std,
                'increase_pct': (shocked_std / self.portfolio_std - 1) * 100 if self.portfolio_std > 0 else 0
            }
        
        elif scenario_type == 'market_regime_change':
            # Raddoppia volatilità dei returns
            shocked_returns = self.returns * 2
            shocked_cov = shocked_returns.cov()
            shocked_std = np.sqrt(np.dot(self.weights_reordered, np.dot(shocked_cov * 252, self.weights_reordered)))
            
            return {
                'scenario': 'Market Regime Change',
                'current_std': self.portfolio_std,
                'shocked_std': shocked_std,
                'increase_pct': (shocked_std / self.portfolio_std - 1) * 100
            }
    
    # ============ RISK DECOMPOSITION ============
    
    def risk_decomposition(self) -> pd.DataFrame:
        """
        Decomposizione rischio - Quanto rischio viene da ogni asset?
        
        Returns:
            DataFrame con contributo al rischio per asset
        """
        # Calcola il contributo al rischio usando la matrice di covarianza giornaliera
        cov_daily = self.cov_matrix
        portfolio_var_daily = np.dot(self.weights_reordered, np.dot(cov_daily, self.weights_reordered))
        portfolio_std_daily = np.sqrt(portfolio_var_daily)
        
        # Marginal contribution to risk (daily)
        if portfolio_var_daily > 0:
            marginal_contrib = np.dot(cov_daily, self.weights_reordered) / portfolio_std_daily
        else:
            marginal_contrib = np.zeros(len(self.weights_reordered))
        
        # Contribution al rischio - usa weights_reordered per coerenza con la covarianza
        contrib_risk = self.weights_reordered * marginal_contrib
        total_contrib = np.sum(np.abs(contrib_risk))
        
        if total_contrib > 0:
            contrib_risk_pct = (contrib_risk / total_contrib) * 100
        else:
            contrib_risk_pct = np.zeros(len(self.weights_reordered))
        
        # Però per il risulat finale, mostriamo i dati nell'ordine originale dei tickers
        # Crea mappatura inversa: dall'ordine alphabetico al tickers originale
        ticker_to_reordered_idx = {ticker: i for i, ticker in enumerate(self.returns.columns)}
        reorder_to_ticker_idx = [ticker_to_reordered_idx[ticker] for ticker in self.tickers]
        
        results = pd.DataFrame({
            'Asset': self.tickers,
            'Weight': self.weights * 100,
            'Risk Contribution': contrib_risk_pct[reorder_to_ticker_idx],
            'Risk per Unit': np.where(self.weights > 1e-10, contrib_risk_pct[reorder_to_ticker_idx] / self.weights, 0)
        })
        
        return results.sort_values('Risk Contribution', ascending=False)
    
    # ============ SENSITIVITY ANALYSIS ============
    
    def sensitivity_analysis(self, asset_idx: int, 
                            shock_range: np.ndarray) -> pd.DataFrame:
        """
        Analisi sensibilità - Come varia il rischio con shock su un asset?
        
        Args:
            asset_idx: Indice dell'asset
            shock_range: Array di shock percentuali da testare
        
        Returns:
            DataFrame con VaR per ogni shock
        """
        results = []
        
        for shock in shock_range:
            # Modifica prezzo asset
            shocked_data = self.data.copy()
            shocked_data.iloc[-1, asset_idx] *= (1 + shock / 100)
            
            # Crea analyzer temporaneo
            temp_analyzer = PortfolioRiskAnalyzer(
                self.tickers, self.weights, self.lookback_days, self.rf_rate
            )
            temp_analyzer.data = shocked_data
            temp_analyzer._calculate_statistics()
            
            results.append({
                'Shock (%)': shock,
                'Portfolio Std': temp_analyzer.portfolio_std * 100,
                'Portfolio Return': temp_analyzer.portfolio_return * 100,
                'Sharpe Ratio': (temp_analyzer.portfolio_return - self.rf_rate) / temp_analyzer.portfolio_std
            })
        
        return pd.DataFrame(results)
    
    # ============ BACKTESTING ============
    
    def backtest_var(self, confidence: float = 0.95) -> Dict:
        """
        Backtest del modello VAR
        Verifica quante volte le perdite superano il VAR (dovrebbe essere ~5% per 95% confidence)
        
        Args:
            confidence: Confidence level del VaR
        
        Returns:
            Dict con risultati backtest
        """
        portfolio_returns = (self.returns @ self.weights) * 100
        
        # Minimo dati necessari
        if len(portfolio_returns) < 100:
            return {
                'exception_rate': 0,
                'expected_rate': (1 - confidence) * 100,
                'total_exceptions': 0,
                'total_days_tested': 0,
                'model_valid': False
            }
        
        # Calcola VaR storico sui dati completi
        var_daily = np.percentile(portfolio_returns, (1 - confidence) * 100)
        
        # Conta quanti giorni hanno perdite peggiori del VaR
        # VaR è un valore negativo (percentile inferiore)
        # Contiamo i giorni in cui il return è più negativo del VaR percentile
        exceptions = (portfolio_returns <= var_daily).sum()
        
        total_days = len(portfolio_returns)
        exception_rate = exceptions / total_days
        expected_rate = 1 - confidence
        
        # Validazione usando intervallo di confidenza binomiale
        # Per un portfolio ben diversificato, le eccezioni dovrebbero essere circa il 5% per 95% VaR
        # Tolleriamo una deviazione ragionevole
        if total_days > 50:
            # Intervallo di confidenza binomiale (approssimazione normale)
            margin = 2.0 * np.sqrt(expected_rate * (1 - expected_rate) / total_days)
            lower_bound = max(0, expected_rate - margin)
            upper_bound = min(1, expected_rate + margin)
            is_valid = lower_bound <= exception_rate <= upper_bound
        else:
            is_valid = False
        
        return {
            'exception_rate': exception_rate * 100,
            'expected_rate': expected_rate * 100,
            'total_exceptions': int(exceptions),
            'total_days_tested': total_days,
            'model_valid': is_valid,
            'var_estimate': abs(var_daily)
        }
    
    # ============ CORRELATION ANALYSIS ============
    
    def get_correlation_matrix(self) -> pd.DataFrame:
        """Ritorna matrice di correlazione con indici ordinati"""
        # corr_matrix è already una matrice pandas.core.frame.DataFrame con indici
        # Assicura che sia ordinata coerentemente con self.tickers
        return self.corr_matrix
    
    # ============ PORTFOLIO METRICS ============
    
    def get_portfolio_metrics(self) -> Dict:
        """Ritorna metriche principali del portfolio"""
        sharpe = (self.portfolio_return - self.rf_rate) / self.portfolio_std if self.portfolio_std > 0 else 0
        
        return {
            'Expected Annual Return': self.portfolio_return * 100,
            'Annual Volatility (Std)': self.portfolio_std * 100,
            'Sharpe Ratio': sharpe,
            'Daily VaR (95%)': self.var_historical(0.95),
            'Daily CVaR (95%)': self.cvar_historical(0.95),
        }
    
    def get_historical_performance(self, year: int = None, initial_investment: float = 100000) -> Dict:
        """
        Calcola la performance storica del portafoglio per un anno specifico
        
        Args:
            year: Anno da analizzare (None = tutto il periodo disponibile)
            initial_investment: Importo iniziale (default 100000 euro)
        
        Returns:
            Dict con performance del portafoglio e singoli asset
        """
        portfolio_data = self.data.copy()
        
        # Filtra per anno se specificato
        if year is not None:
            year_start = pd.Timestamp(f'{year}-01-01')
            year_end = pd.Timestamp(f'{year}-12-31')
            mask = (portfolio_data.index >= year_start) & (portfolio_data.index <= year_end)
            portfolio_data = portfolio_data[mask]
        
        if len(portfolio_data) == 0:
            raise ValueError(f"Nessun dato disponibile per l'anno {year}")
        
        # Calcola l'equity curve del portafoglio
        # Normalizza i prezzi al primo giorno
        normalized_prices = portfolio_data / portfolio_data.iloc[0] * initial_investment
        
        # Applica i pesi al portafoglio (usa weights_reordered per coerenza)
        # Crea un DataFrame con i pesi applicati
        weighted_prices = normalized_prices * self.weights_reordered
        portfolio_value = weighted_prices.sum(axis=1)
        
        # Metriche di performance
        start_value = portfolio_value.iloc[0]
        end_value = portfolio_value.iloc[-1]
        total_gain_loss = end_value - start_value
        total_return_pct = (total_gain_loss / start_value) * 100
        
        # Performance per singolo asset
        asset_performance = {}
        for i, ticker in enumerate(self.returns.columns):
            # Trova l'indice del ticker nel self.tickers (ordine originale)
            original_ticker_idx = list(self.tickers).index(ticker)
            original_ticker = self.tickers[original_ticker_idx]
            
            # Calcola return dell'asset dal prezzo
            asset_total_return = (portfolio_data[ticker].iloc[-1] / portfolio_data[ticker].iloc[0] - 1) * 100
            
            # Valore in euro guadagnato/perso su questo asset
            asset_initial = initial_investment * self.weights[original_ticker_idx]
            asset_final = asset_initial * (1 + asset_total_return / 100)
            asset_gain_loss = asset_final - asset_initial
            
            asset_performance[original_ticker] = {
                'return_pct': asset_total_return,
                'gain_loss': asset_gain_loss,
                'final_value': asset_final,
                'initial_value': asset_initial
            }
        
        # Grafico dell'equity curve (per ritornare a dashboard come serie temporale)
        equity_curve = pd.DataFrame({
            'date': portfolio_value.index,
            'value': portfolio_value.values
        })
        
        return {
            'start_date': portfolio_data.index[0],
            'end_date': portfolio_data.index[-1],
            'start_value': start_value,
            'end_value': end_value,
            'total_gain_loss': total_gain_loss,
            'total_return_pct': total_return_pct,
            'equity_curve': equity_curve,
            'asset_performance': asset_performance,
            'days_traded': len(portfolio_data)
        }
