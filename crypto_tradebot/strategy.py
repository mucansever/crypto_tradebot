from numpy.core.numeric import NaN
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import btalib

class Strategy:
    def __init__(self, indicator, strategy, symbol, trade_interval, klines: pd.DataFrame):
        self.indicator = indicator
        self.strategy = strategy
        self.symbol = symbol
        self.trade_interval = trade_interval
        self.klines = klines
        self.calculate_indicator()
        self.result = self.calculate_strategy()

    def get_indicator(self):
        return self.indicator
    
    def get_strategy(self):
        return self.strategy

    def get_symbol(self):
        return self.symbol

    def get_trade_interval(self):
        return self.trade_interval

    def get_dataframe(self):
        return self.klines

    def get_result(self):
        return self.result

    def calculate_indicator(self):
        # Calculate indicator and append to dataframe
        if self.indicator == 'RSI':
            self.klines['rsi'] = btalib.rsi(self.klines.close, period=15).df
        elif self.indicator == 'SMA':
            self.klines['12sma'] = btalib.sma(self.klines.close, period=12).df
            self.klines['50sma'] = btalib.sma(self.klines.close, period=50).df
        elif self.indicator == 'MACD':
            self.klines['macd'],self.klines['macdSignal'],self.klines['macdHist'] = btalib.macd(self.klines.close, pfast=12, pslow=26, psignal=9)
        else:
            return None

    def calculate_strategy(self):
        if self.indicator == 'MACD' and self.strategy == 'CROSSOVER':
            crosses = []
            macd_greater = False
            for i in range(len(self.klines.macd)):
                # If both MACD and MACDSignal are not NaN
                if not np.isnan(self.klines.macd[i]) and not np.isnan(self.klines.macdSignal[i]):
                    # Bearish Signal
                    if self.klines.macd[i] > self.klines.macdSignal[i] and not macd_greater:
                        cross = [self.klines.index[i], self.klines.macd[i], 'BUY', self.klines.close[i]]
                        macd_greater = True
                    # Bullish Signal
                    elif self.klines.macd[i] <= self.klines.macdSignal[i] and macd_greater:
                        cross = [self.klines.index[i], self.klines.macd[i], 'SELL', self.klines.close[i]]
                        macd_greater = False
                    else:
                        continue
                    crosses.append(cross)
            return np.array(crosses)
        elif self.indicator == 'RSI' and self.strategy == 'OVERBOUGHT':
            operations = []
            for i in range(len(self.klines.rsi)):
                if not np.isnan(self.klines.rsi[i]):
                    # RSI over 70, overbought
                    if self.klines.rsi[i] > 70:
                        operation = [self.klines.index[i], self.klines.rsi[i], 'SELL', self.klines.close[i]]
                    # RSI below 30, oversold
                    elif self.klines.rsi[i] < 30:
                        operation = [self.klines.index[i], self.klines.rsi[i], 'BUY', self.klines.close[i]]
                    else:
                        continue
                    operations.append(operation)
            return np.array(operations)
        elif self.indicator == 'SMA' and self.strategy == 'CROSSOVER':
            crosses = []
            greater_sma = False
            for i in range(len(self.klines['12sma'])):
                # If both 12sma and 20sma are not NaN
                if not np.isnan(self.klines['12sma'][i]) and not np.isnan(self.klines['50sma'][i]):
                    # Bearish signal
                    if self.klines['12sma'][i] > self.klines['50sma'][i] and not greater_sma:
                        cross = [self.klines.index[i], self.klines['12sma'][i], 'BUY', self.klines.close[i]]
                        greater_sma = True
                    # Bullish signal
                    elif self.klines['12sma'][i] <= self.klines['50sma'][i] and greater_sma:
                        cross = [self.klines.index[i], self.klines['12sma'][i], 'SELL', self.klines.close[i]]
                        greater_sma = False
                    else:
                        continue
                    crosses.append(cross)
            return np.array(crosses)
        
    def plotIndicator(self):
        plt.style.use('dark_background')
        plt.title(self.indicator + " Plot for " + self.symbol + " on " + self.trade_interval)
        plt.xlabel("Open Time")
        plt.ylabel("Value")
        if self.indicator == 'MACD':
            plt.plot(self.klines.index, self.klines.macd, label='MACD')
            plt.plot(self.klines.index, self.klines.macdSignal, label='MACD Signal')
            plt.plot(self.klines.index, self.klines.macdHist, label='MACD Histogram')
            for cross in self.result:
                plt.plot(cross[0], cross[1], ('go' if cross[2]=='BUY' else 'ro'))            
            plt.legend()
            plt.show()
        elif self.indicator == 'RSI':
            plt.plot(self.klines.index, self.klines.rsi, label='RSI')
            plt.axhline(y=70, xmin=0, xmax=1,color='r',linestyle='--',label='Overbought')
            plt.axhline(y=30, xmin=0, xmax=1,color='g',linestyle='--',label='Oversold')
            plt.legend()
            plt.show()
        elif self.indicator == 'SMA':
            plt.plot(self.klines.index, self.klines['12sma'], label='12 SMA')
            plt.plot(self.klines.index, self.klines['50sma'], label='50 SMA')
            for cross in self.result:
                plt.plot(cross[0], cross[1], ('go' if cross[2]=='BUY' else 'ro'))
            plt.legend()
            plt.show()
