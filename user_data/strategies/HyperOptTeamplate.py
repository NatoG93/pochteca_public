"""
HyperOptTemplate.py
=================
Dentro de la carpeta user_data/strategies

docker compose run --rm freqtrade hyperopt --strategy Pochteca_Hyper --hyperopt-loss SharpeHyperOptLoss --timerange 20251001- --timeframe 15m -e 50 --spaces buy

"""
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, CategoricalParameter
from pandas import DataFrame
import talib.abstract as ta

class TemplateHyperopt(IStrategy):
    # 1. Definir el Timeframe
    timeframe = '15m'

    # 2. DEFINIR LAS "PERILLAS" (Parámetros)
    # IntParameter(mínimo, máximo, default, space)
    buy_ema_fast = IntParameter(5, 15, default=9, space='buy')
    buy_ema_slow = IntParameter(20, 45, default=21, space='buy')
    
    # DecimalParameter(mínimo, máximo, default, space)
    buy_rsi_low = IntParameter(20, 40, default=30, space='buy')
    
    # CategoricalParameter: Elige entre opciones específicas
    buy_trigger = CategoricalParameter(['rsi', 'ema', 'both'], default='ema', space='buy')

    # Parámetros de Salida (Opcional optimizarlos también)
    sell_rsi_high = IntParameter(70, 90, default=80, space='sell')

    # Configuración base
    minimal_roi = {"0": 0.10}
    stoploss = -0.10
    trailing_stop = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # AQUÍ CALCULAMOS TODO LO QUE LOS PARÁMETROS PODRÍAN NECESITAR
        # Si vas a optimizar periodos de EMA, calculamos un rango o los valores base
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=self.buy_ema_fast.value)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=self.buy_ema_slow.value)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['ema_200'] = ta.EMA(dataframe, timeperiod=200)
        
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # USAMOS .value PARA QUE FREQTRADE SEPA QUÉ PROBAR
        dataframe.loc[
            (
                (dataframe['ema_fast'] > dataframe['ema_slow']) &
                (dataframe['rsi'] > self.buy_rsi_low.value) &
                (dataframe['close'] > dataframe['ema_200'])
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] > self.sell_rsi_high.value)
            ),
            'exit_long'] = 1
        return dataframe
