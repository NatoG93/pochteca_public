"""
EMA Scalping Strategy v1.0
==========================
Estrategia inicial para Renato - Pochteca Algotrading Project

Tipo: Scalping → Swing
Timeframe recomendado: 15m, 1h
Mercado: Crypto (BTC, ETH, majors)

Lógica:
- Entry: EMA 9 cruza por encima de EMA 21 + RSI < 70 (no sobrecomprado)
- Exit: EMA 9 cruza por debajo de EMA 21 O RSI > 80 O take profit/stop loss

Risk Management:
- Stop Loss: 2%
- Take Profit: 4% (2:1 risk/reward)
- Trailing Stop: 1% después de 2% profit
"""

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import talib.abstract as ta


class EMAScalpingStrategy(IStrategy):
    """
    Estrategia de scalping basada en cruces de EMA con filtro RSI.
    Diseñada para timeframes de 15m a 1h.
    """

    # Configuración de timeframe
    timeframe = '15m'

    # ROI (Return on Investment) - Take profits escalonados
    minimal_roi = {
        "0": 0.04,      # 4% inmediato
        "30": 0.03,     # 3% después de 30 minutos
        "60": 0.02,     # 2% después de 1 hora
        "120": 0.01     # 1% después de 2 horas
    }

    # Stop Loss
    stoploss = -0.02  # -2%

    # Trailing Stop - Se activa después de cierto profit
    trailing_stop = True
    trailing_stop_positive = 0.01       # Se activa al 1% de profit
    trailing_stop_positive_offset = 0.02  # Offset del 2%
    trailing_only_offset_is_reached = True

    # Configuración de órdenes
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Protección contra pérdidas consecutivas
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Parámetros optimizables (para hyperopt después)
    # Parámetros optimizables (para hyperopt después)
    buy_ema_fast = IntParameter(5, 15, default=9, space='buy', optimize=True)
    buy_ema_slow = IntParameter(15, 30, default=21, space='buy', optimize=True)
    buy_rsi_period = IntParameter(10, 20, default=14, space='buy', optimize=True)
    buy_rsi_threshold = IntParameter(30, 50, default=40, space='buy', optimize=True)
    sell_rsi_threshold = IntParameter(70, 90, default=80, space='sell', optimize=True)

    # Información de la estrategia
    def informative_pairs(self):
        """
        Pares adicionales para analizar (por ejemplo, BTC para correlación)
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Calcula los indicadores técnicos necesarios.
        """
        # EMAs
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=self.buy_ema_fast.value)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=self.buy_ema_slow.value)
        
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.buy_rsi_period.value)
        
        # Bollinger Bands (para referencia visual y posibles mejoras)
        bollinger = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe['bb_upper'] = bollinger['upperband']
        dataframe['bb_middle'] = bollinger['middleband']
        dataframe['bb_lower'] = bollinger['lowerband']
        
        # MACD (para confirmación adicional)
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macd_signal'] = macd['macdsignal']
        dataframe['macd_hist'] = macd['macdhist']
        
        # ATR para volatilidad
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        
        # Volume SMA para filtrar trades en baja liquidez
        dataframe['volume_sma'] = ta.SMA(dataframe['volume'], timeperiod=20)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Define las condiciones de entrada (compra).
        """
        dataframe.loc[
            (
                # Cruce de EMA: rápida cruza por encima de lenta
                (dataframe['ema_fast'] > dataframe['ema_slow']) &
                (dataframe['ema_fast'].shift(1) <= dataframe['ema_slow'].shift(1)) &
                
                # RSI no sobrecomprado
                (dataframe['rsi'] < 70) &
                (dataframe['rsi'] > self.buy_rsi_threshold.value) &
                
                # Volumen por encima del promedio (confirmación)
                (dataframe['volume'] > dataframe['volume_sma'] * 0.5) &
                
                # Volumen no es cero
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Define las condiciones de salida (venta).
        """
        dataframe.loc[
            (
                # Cruce de EMA: rápida cruza por debajo de lenta
                (
                    (dataframe['ema_fast'] < dataframe['ema_slow']) &
                    (dataframe['ema_fast'].shift(1) >= dataframe['ema_slow'].shift(1))
                ) |
                # O RSI sobrecomprado
                (dataframe['rsi'] > self.sell_rsi_threshold.value)
            ),
            'exit_long'] = 1

        return dataframe

    def custom_exit(self, pair: str, trade, current_time, current_rate,
                    current_profit, **kwargs):
        """
        Lógica de salida personalizada.
        Útil para implementar lógica más compleja después.
        """
        # Ejemplo: Si el profit es mayor al 5%, salir inmediatamente
        if current_profit > 0.05:
            return "take_profit_5pct"
        
        # Ejemplo: Si llevamos más de 4 horas y estamos en profit, salir
        if (current_time - trade.open_date_utc).seconds > 14400 and current_profit > 0:
            return "timeout_with_profit"
        
        return None

    def leverage(self, pair: str, current_time, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag,
                 side: str, **kwargs) -> float:
        """
        Define el apalancamiento. Por ahora usamos 1x (spot).
        Cuando estés listo para futuros, esto se puede modificar.
        """
        return 1.0
