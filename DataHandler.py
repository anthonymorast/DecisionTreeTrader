import requests

class TimeFrame:
    ONE_MINUTE = '1min' 
    FIVE_MINUTE = '5min'
    FIFTEEN_MINUTE = '15min'
    THIRTY_MINUTE = '30min'
    ONE_HOUR = '1hour'
    FOUR_HOUR = '4hour'
    ONE_DAY = '1day'

class Indicators:
    EMA = "ema"
    SMA = "sma"
    WMA = "wma"
    TEMA = "tema"
    DEMA = "dema"
    WILLIAMS = "williams"
    RSI = "rsi"
    ADX = "adx"
    STANDARD_DEVATION = "standardDeviation"

    def EmaIndicators():
        return [Indicators.EMA, Indicators.SMA, Indicators.TEMA, Indicators.DEMA, Indicators.WMA]

    def AllIndicators():
        return [Indicators.EMA, Indicators.SMA, Indicators.WMA, Indicators.TEMA, Indicators.DEMA, Indicators.WILLIAMS, Indicators.RSI, Indicators.ADX, Indicators.STANDARD_DEVATION]

class DataHandler:
    def __init__(self, apiKey : str):
        self.baseurl = 'https://financialmodelingprep.com/api/v3'
        self.apikey = apiKey

    def __process_get_request(self, url : str) -> dict:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json()
        else: 
            print(f"GET request url={url} returned status code={res.status_code}")
        return {}        

    def IndicatorDataByName(self, symbol : str, period : int, timeframe : str, fromdt : str, todt : str, type : str):
        return self.__process_get_request(f"{self.baseurl}/technical_indicator/{timeframe}/{symbol}?type={type}&period={str(period)}&apikey={self.apikey}&from={fromdt}&to={todt}")

    def EMA(self, symbol : str, period : int, timeframe : str, fromdt : str, todt : str):
        return self.IndicatorDataByName(symbol, period, timeframe, "ema", todt, fromdt)

    def SMA(self, symbol : str, period : int, timeframe : str, fromdt : str, todt : str):
        return self.IndicatorDataByName(symbol, period, timeframe, "sma", todt, fromdt)
    
    def WMA(self, symbol : str, period : int, timeframe : str, fromdt : str, todt : str):
        return self.IndicatorDataByName(symbol, period, timeframe, "wma", todt, fromdt)
    
    def TripleEMA(self, symbol : str, period : int, timeframe : str, fromdt : str, todt : str):
        return self.IndicatorDataByName(symbol, period, timeframe, "tema", todt, fromdt)
    
    def DoubleEMA(self, symbol : str, period : int, timeframe : str, fromdt : str, todt : str):
        return self.IndicatorDataByName(symbol, period, timeframe, "dema", todt, fromdt)
    
    def Williams(self, symbol : str, period : int, timeframe : str, fromdt : str, todt : str):
        return self.IndicatorDataByName(symbol, period, timeframe, "williams", todt, fromdt)
    
    def RSI(self, symbol : str, period : int, timeframe : str, fromdt : str, todt : str):
        return self.IndicatorDataByName(symbol, period, timeframe, "rsi", todt, fromdt)
    
    def ADX(self, symbol : str, period : int, timeframe : str, fromdt : str, todt : str):
        return self.IndicatorDataByName(symbol, period, timeframe, "adx", todt, fromdt)
    
    def StandardDeviation(self, symbol : str, period : int, timeframe : str, fromdt : str, todt : str):
        return self.IndicatorDataByName(symbol, period, timeframe, "standardDeviation", todt, fromdt)
    
    def HistoricalData(self, symbol : str, startDate : str, endDate : str, timeframe : str = TimeFrame.ONE_DAY):
        return self.__process_get_request(f"{self.baseurl}/historical-chart/{timeframe}/{symbol}?from={startDate}&to={endDate}&apikey={self.apikey}")
