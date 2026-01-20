"""
Weapon Candle Strategy v1.0
============================
Basado en research paper: "Synergizing quantitative finance models 
and market microstructure analysis for enhanced algorithmic trading strategies"

Resultados documentados:
- 60.63% profitable trades
- Profit Factor: 1.882
- Tested en NSE India

Indicadores:
- RSI (14) - Momentum y overbought/oversold
- EMA (9, 21) - Trend direction
- VWAP - Volume-weighted fair value
- MACD (12, 26, 9) - Momentum confirmation

Lógica:
- LONG: Price > VWAP + EMA bullish + MACD bullish + RSI not overbought
- SHORT: Price < VWAP + EMA bearish + MACD bearish + RSI not oversold
"""

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import talib.abstract as ta
import numpy as np


class WeaponCandleStrategy(IStrategy):
    """
    Estrategia de 4 indicadores combinados basada en research académico.
    Win rate documentado: 60.63%, Profit Factor: 1.882
    """

    # Timeframe - El paper usó daily, pero adaptamos a 1h para scalping→swing
    timeframe = '1h'

    # ROI escalonado
    minimal_roi = {
        "0": 0.05,      # 5% inmediato
        "60": 0.04,     # 4% después de 1 hora
        "180": 0.03,    # 3% después de 3 horas
        "360": 0.02,    # 2% después de 6 horas
        "720": 0.01     # 1% después de 12 horas
    }

    # Stop Loss más conservador para prop firms
    stoploss = -0.03  # -3%

    # Trailing stop
    trailing_stop = True
    trailing_stop_positive = 0.015
    trailing_stop_positive_offset = 0.025
    trailing_only_offset_is_reached = True

    # Configuración de órdenes
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': True
    }

    # Parámetros optimizables
    # EMA
    buy_ema_fast = IntParameter(5, 15, default=9, space='buy', optimize=True)
    buy_ema_slow = IntParameter(15, 30, default=21, space='buy', optimize=True)
    
    # RSI
    buy_rsi_period = IntParameter(10, 20, default=14, space='buy', optimize=True)
    buy_rsi_lower = IntParameter(30, 50, default=40, space='buy', optimize=True)
    buy_rsi_upper = IntParameter(60, 75, default=70, space='buy', optimize=True)
    sell_rsi_threshold = IntParameter(70, 85, default=75, space='sell', optimize=True)
    
    # MACD
    buy_macd_fast = IntParameter(8, 15, default=12, space='buy', optimize=True)
    buy_macd_slow = IntParameter(20, 30, default=26, space='buy', optimize=True)
    buy_macd_signal = IntParameter(7, 12, default=9, space='buy', optimize=True)

    # Para calcular VWAP manualmente (Freqtrade no lo tiene built-in)
    buy_vwap_period = IntParameter(14, 30, default=20, space='buy', optimize=True)

    def calculate_vwap(self, dataframe: DataFrame, period: int = 20) -> DataFrame:
        """
        Calcula VWAP rolling (Volume Weighted Average Price)
        """
        typical_price = (dataframe['high'] + dataframe['low'] + dataframe['close']) / 3
        vwap = (typical_price * dataframe['volume']).rolling(window=period).sum() / \
               dataframe['volume'].rolling(window=period).sum()
        return vwap

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Calcula los 4 indicadores del Weapon Candle Strategy
        """
        # ==========================================
        # 1. EMAs (Trend Direction)
        # ==========================================
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=self.buy_ema_fast.value)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=self.buy_ema_slow.value)
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema_200'] = ta.EMA(dataframe, timeperiod=200)
        
        # EMA Trend Signal
        dataframe['ema_bullish'] = (
            (dataframe['ema_fast'] > dataframe['ema_slow']) &
            (dataframe['close'] > dataframe['ema_fast'])
        ).astype(int)
        
        dataframe['ema_bearish'] = (
            (dataframe['ema_fast'] < dataframe['ema_slow']) &
            (dataframe['close'] < dataframe['ema_fast'])
        ).astype(int)

        # ==========================================
        # 2. VWAP (Volume-Weighted Fair Value)
        # ==========================================
        dataframe['vwap'] = self.calculate_vwap(dataframe, self.buy_vwap_period.value)
        
        # VWAP Signal
        dataframe['above_vwap'] = (dataframe['close'] > dataframe['vwap']).astype(int)
        dataframe['below_vwap'] = (dataframe['close'] < dataframe['vwap']).astype(int)

        # ==========================================
        # 3. MACD (Momentum Confirmation)
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
        
        # MACD Signal
        dataframe['macd_bullish'] = (
            (dataframe['macd'] > dataframe['macd_signal']) &
            (dataframe['macd_hist'] > 0)
        ).astype(int)
        
        dataframe['macd_bearish'] = (
            (dataframe['macd'] < dataframe['macd_signal']) &
            (dataframe['macd_hist'] < 0)
        ).astype(int)

        # ==========================================
        # 4. RSI (Overbought/Oversold Filter)
        # ==========================================
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.buy_rsi_period.value)
        
        # RSI zones
        dataframe['rsi_ok_buy'] = (
            (dataframe['rsi'] > self.buy_rsi_lower.value) &
            (dataframe['rsi'] < self.buy_rsi_upper.value)
        ).astype(int)
        
        dataframe['rsi_oversold'] = (dataframe['rsi'] < self.buy_rsi_lower.value).astype(int)
        dataframe['rsi_overbought'] = (dataframe['rsi'] > self.sell_rsi_threshold.value).astype(int)

        # ==========================================
        # 5. Señal Combinada (Weapon Score)
        # ==========================================
        # Score de 0-4 basado en cuántos indicadores confirman
        dataframe['weapon_score_long'] = (
            dataframe['ema_bullish'] +
            dataframe['above_vwap'] +
            dataframe['macd_bullish'] +
            dataframe['rsi_ok_buy']
        )
        
        dataframe['weapon_score_short'] = (
            dataframe['ema_bearish'] +
            dataframe['below_vwap'] +
            dataframe['macd_bearish'] +
            (1 - dataframe['rsi_overbought'])  # RSI no overbought
        )

        # ==========================================
        # Indicadores adicionales para análisis
        # ==========================================
        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe['bb_upper'] = bollinger['upperband']
        dataframe['bb_middle'] = bollinger['middleband']
        dataframe['bb_lower'] = bollinger['lowerband']
        
        # ATR para volatilidad
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        dataframe['atr_pct'] = dataframe['atr'] / dataframe['close'] * 100
        
        # Volume analysis
        dataframe['volume_sma'] = ta.SMA(dataframe['volume'], timeperiod=20)
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_sma']

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Señal de entrada: Los 4 indicadores deben confirmar (Weapon Score = 4)
        """
        dataframe.loc[
            (
                # Weapon Score máximo (todos los indicadores confirman)
                (dataframe['weapon_score_long'] >= 4) &
                
                # Confirmación adicional: Precio subiendo
                (dataframe['close'] > dataframe['open']) &
                
                # Volumen decente
                (dataframe['volume_ratio'] > 0.5) &
                
                # No en zona de resistencia extrema
                (dataframe['close'] < dataframe['bb_upper']) &
                
                # Volumen no es cero
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Señal de salida: Cualquier indicador se vuelve bearish
        """
        dataframe.loc[
            (
                # EMA cruce bearish
                (
                    (dataframe['ema_fast'] < dataframe['ema_slow']) &
                    (dataframe['ema_fast'].shift(1) >= dataframe['ema_slow'].shift(1))
                ) |
                # RSI overbought
                (dataframe['rsi'] > self.sell_rsi_threshold.value) |
                # MACD bearish crossover
                (
                    (dataframe['macd'] < dataframe['macd_signal']) &
                    (dataframe['macd'].shift(1) >= dataframe['macd_signal'].shift(1))
                ) |
                # Precio cae debajo de VWAP
                (
                    (dataframe['close'] < dataframe['vwap']) &
                    (dataframe['close'].shift(1) >= dataframe['vwap'].shift(1))
                )
            ),
            'exit_long'] = 1

        return dataframe

    def custom_stoploss(self, pair: str, trade, current_time, current_rate,
                        current_profit, **kwargs) -> float:
        """
        Stop loss dinámico basado en ATR
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        
        if len(dataframe) > 0:
            last_candle = dataframe.iloc[-1]
            atr_pct = last_candle['atr_pct']
            
            # Stop loss = 2x ATR pero mínimo -2% y máximo -5%
            dynamic_sl = -(atr_pct * 2) / 100
            return max(min(dynamic_sl, -0.02), -0.05)
        
        return -0.03  # Default 3%

    def custom_exit(self, pair: str, trade, current_time, current_rate,
                    current_profit, **kwargs):
        """
        Lógica de salida personalizada para maximizar ganancias
        """
        # Take profit agresivo si el profit es muy alto
        if current_profit > 0.08:  # +8%
            return "take_profit_8pct"
        
        # Salir si llevamos mucho tiempo con profit pequeño
        trade_duration = (current_time - trade.open_date_utc).total_seconds() / 3600
        
        if trade_duration > 24 and current_profit > 0.02:
            return "timeout_profit_24h"
        
        if trade_duration > 48 and current_profit > 0:
            return "timeout_profit_48h"
        
        return None

    def leverage(self, pair: str, current_time, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag,
                 side: str, **kwargs) -> float:
        """
        Apalancamiento conservador para prop firms
        """
        return 1.0  # Spot only para empezar
