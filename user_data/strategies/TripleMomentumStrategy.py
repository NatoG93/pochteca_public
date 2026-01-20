"""
Triple Momentum Strategy v1.0
==============================
Basado en: "73% Win Rate Stochastic RSI and MACD Strategy"

Resultados documentados:
- Win rate: 52-73% (depende de condiciones de mercado)
- Average gain: 0.88% per trade
- Tested en forex majors (EUR/USD, GBP/USD, USD/JPY)

Indicadores:
- Stochastic RSI (14, 3, 3) - Timing de entrada
- MACD (12, 26, 9) - Trend confirmation
- RSI (14) - Momentum filter

Lógica:
- LONG: Stoch RSI oversold + MACD bullish crossover + RSI rising
- Exit: MACD bearish crossover
"""

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import talib.abstract as ta
import numpy as np


class TripleMomentumStrategy(IStrategy):
    """
    Estrategia de triple confirmación con Stochastic RSI + MACD + RSI
    Win rate documentado: 52-73%
    """

    # Timeframe recomendado del paper: 15m, 30m, 1h
    timeframe = '15m'

    # ROI conservador
    minimal_roi = {
        "0": 0.03,      # 3% inmediato
        "30": 0.025,    # 2.5% después de 30 min
        "60": 0.02,     # 2% después de 1 hora
        "120": 0.015,   # 1.5% después de 2 horas
        "240": 0.01     # 1% después de 4 horas
    }

    # Stop Loss
    stoploss = -0.02  # -2% (tight para scalping)

    # Trailing stop agresivo
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True

    # Configuración
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': True
    }

    # Usar exit signals
    use_exit_signal = True
    exit_profit_only = False

    # ==========================================
    # Parámetros del paper
    # ==========================================
    # Stochastic RSI
    buy_stoch_rsi_period = IntParameter(10, 20, default=14, space='buy', optimize=True)
    buy_stoch_k_period = IntParameter(2, 5, default=3, space='buy', optimize=True)
    buy_stoch_d_period = IntParameter(2, 5, default=3, space='buy', optimize=True)
    buy_stoch_oversold = IntParameter(15, 30, default=20, space='buy', optimize=True)
    sell_stoch_overbought = IntParameter(70, 85, default=80, space='sell', optimize=True)
    
    # MACD
    buy_macd_fast = IntParameter(10, 14, default=12, space='buy', optimize=True)
    buy_macd_slow = IntParameter(24, 28, default=26, space='buy', optimize=True)
    buy_macd_signal = IntParameter(7, 11, default=9, space='buy', optimize=True)
    
    # RSI
    buy_rsi_period = IntParameter(12, 16, default=14, space='buy', optimize=True)
    buy_rsi_threshold = IntParameter(45, 55, default=50, space='buy', optimize=True)

    def calculate_stochastic_rsi(self, dataframe: DataFrame, 
                                  rsi_period: int = 14,
                                  stoch_period: int = 14,
                                  k_period: int = 3,
                                  d_period: int = 3) -> tuple:
        """
        Calcula Stochastic RSI
        """
        # Calcular RSI primero
        rsi = ta.RSI(dataframe, timeperiod=rsi_period)
        
        # Aplicar Stochastic al RSI
        rsi_min = rsi.rolling(window=stoch_period).min()
        rsi_max = rsi.rolling(window=stoch_period).max()
        
        # Stoch K
        stoch_rsi_k = 100 * (rsi - rsi_min) / (rsi_max - rsi_min + 0.0001)
        
        # Stoch D (SMA de K)
        stoch_rsi_d = stoch_rsi_k.rolling(window=d_period).mean()
        
        # Suavizar K también
        stoch_rsi_k = stoch_rsi_k.rolling(window=k_period).mean()
        
        return stoch_rsi_k, stoch_rsi_d

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Calcula los 3 indicadores del Triple Momentum Strategy
        """
        # ==========================================
        # 1. Stochastic RSI (Timing)
        # ==========================================
        stoch_k, stoch_d = self.calculate_stochastic_rsi(
            dataframe,
            rsi_period=self.buy_stoch_rsi_period.value,
            stoch_period=self.buy_stoch_rsi_period.value,
            k_period=self.buy_stoch_k_period.value,
            d_period=self.buy_stoch_d_period.value
        )
        dataframe['stoch_rsi_k'] = stoch_k
        dataframe['stoch_rsi_d'] = stoch_d
        
        # Stoch RSI signals
        dataframe['stoch_oversold'] = (dataframe['stoch_rsi_k'] < self.buy_stoch_oversold.value).astype(int)
        dataframe['stoch_overbought'] = (dataframe['stoch_rsi_k'] > self.sell_stoch_overbought.value).astype(int)
        
        # Stoch RSI crossover (K crosses above D)
        dataframe['stoch_bullish_cross'] = (
            (dataframe['stoch_rsi_k'] > dataframe['stoch_rsi_d']) &
            (dataframe['stoch_rsi_k'].shift(1) <= dataframe['stoch_rsi_d'].shift(1))
        ).astype(int)
        
        dataframe['stoch_bearish_cross'] = (
            (dataframe['stoch_rsi_k'] < dataframe['stoch_rsi_d']) &
            (dataframe['stoch_rsi_k'].shift(1) >= dataframe['stoch_rsi_d'].shift(1))
        ).astype(int)

        # ==========================================
        # 2. MACD (Trend Confirmation)
        # ==========================================
        macd = ta.MACD(
            dataframe,
            fastperiod=self.buy_macd_fast.value,
            slowperiod=self.buy_macd_slow.value,
            signalperiod=self.buy_macd_signal.value
        )
        dataframe['macd'] = macd['macd']
        dataframe['macd_signal'] = macd['macdsignal']
        dataframe['macd_hist'] = macd['macdhist']
        
        # MACD crossovers
        dataframe['macd_bullish_cross'] = (
            (dataframe['macd'] > dataframe['macd_signal']) &
            (dataframe['macd'].shift(1) <= dataframe['macd_signal'].shift(1))
        ).astype(int)
        
        dataframe['macd_bearish_cross'] = (
            (dataframe['macd'] < dataframe['macd_signal']) &
            (dataframe['macd'].shift(1) >= dataframe['macd_signal'].shift(1))
        ).astype(int)
        
        # MACD bullish (line above signal)
        dataframe['macd_bullish'] = (dataframe['macd'] > dataframe['macd_signal']).astype(int)

        # ==========================================
        # 3. RSI (Momentum Filter)
        # ==========================================
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.buy_rsi_period.value)
        
        # RSI rising
        dataframe['rsi_rising'] = (dataframe['rsi'] > dataframe['rsi'].shift(1)).astype(int)
        dataframe['rsi_above_threshold'] = (dataframe['rsi'] > self.buy_rsi_threshold.value).astype(int)

        # ==========================================
        # Triple Confirmation Score
        # ==========================================
        # Score de 0-3 para entrada
        dataframe['triple_score'] = (
            dataframe['stoch_oversold'] +  # Stoch RSI oversold
            dataframe['macd_bullish'] +     # MACD bullish
            dataframe['rsi_rising']         # RSI rising
        )

        # ==========================================
        # Indicadores adicionales
        # ==========================================
        # EMAs para contexto
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        
        # ATR para sizing
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        
        # Volume
        dataframe['volume_sma'] = ta.SMA(dataframe['volume'], timeperiod=20)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Triple confirmation entry:
        1. Stochastic RSI in oversold zone OR bullish crossover
        2. MACD line above signal (bullish)
        3. RSI rising and above threshold
        """
        dataframe.loc[
            (
                # Condición 1: Stoch RSI oversold O crossover bullish reciente
                (
                    (dataframe['stoch_rsi_k'] < self.buy_stoch_oversold.value) |
                    (dataframe['stoch_bullish_cross'] == 1) |
                    (dataframe['stoch_bullish_cross'].shift(1) == 1) |
                    (dataframe['stoch_bullish_cross'].shift(2) == 1)
                ) &
                
                # Condición 2: MACD bullish
                (dataframe['macd_bullish'] == 1) &
                
                # Condición 3: RSI confirmando momentum
                (dataframe['rsi_rising'] == 1) &
                (dataframe['rsi'] > 40) &
                (dataframe['rsi'] < 70) &
                
                # Filtro adicional: Precio sobre EMA 20
                (dataframe['close'] > dataframe['ema_20']) &
                
                # Volumen decente
                (dataframe['volume'] > dataframe['volume_sma'] * 0.5) &
                
                # Volumen no cero
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Exit según el paper: MACD crossover bearish
        """
        dataframe.loc[
            (
                # Condición principal: MACD bearish crossover
                (dataframe['macd_bearish_cross'] == 1) |
                
                # O Stoch RSI overbought + crossover bearish
                (
                    (dataframe['stoch_rsi_k'] > self.sell_stoch_overbought.value) &
                    (dataframe['stoch_bearish_cross'] == 1)
                ) |
                
                # O RSI extremadamente overbought
                (dataframe['rsi'] > 85)
            ),
            'exit_long'] = 1

        return dataframe

    def custom_exit(self, pair: str, trade, current_time, current_rate,
                    current_profit, **kwargs):
        """
        Exit personalizado para maximizar el average gain de 0.88%
        """
        # El paper muestra 0.88% average gain, así que aim higher
        if current_profit > 0.015:  # 1.5%
            dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
            if len(dataframe) > 0:
                last = dataframe.iloc[-1]
                # Si MACD empieza a debilitarse, salir con profit
                if last['macd_hist'] < dataframe.iloc[-2]['macd_hist']:
                    return "macd_weakening_profit"
        
        # Quick scalp exit
        if current_profit > 0.01:  # 1%
            trade_duration = (current_time - trade.open_date_utc).total_seconds() / 60
            if trade_duration > 30:  # 30 minutos
                return "quick_scalp_1pct"
        
        return None

    def leverage(self, pair: str, current_time, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag,
                 side: str, **kwargs) -> float:
        """
        Sin apalancamiento para empezar
        """
        return 1.0
