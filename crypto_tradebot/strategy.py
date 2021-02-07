import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import btalib

class Strategy:
    def __init__(self, indicator, strategy, tradePair, tradeInterval, klinesDf: pd.DataFrame):
        self.indicator = indicator
        self.strategy = strategy
        self.tradePair = tradePair
        self.tradeInterval = tradeInterval
        self.klinesDf = klinesDf
        self.calculateIndicator()
        self.strategyResult = self.calculateStrategy()

    def getIndicator(self):
        return self.indicator
    
    def getStrategy(self):
        return self.strategy

    def getTradePair(self):
        return self.tradePair

    def getTradeInterval(self):
        return self.tradeInterval

    def getDataframe(self):
        return self.klinesDf

    def getResult(self):
        return self.strategyResult

    def calculateIndicator(self):
        # Calculate indicator and append to dataframe
        if self.indicator == 'RSI':
            self.klinesDf['rsi'] = btalib.rsi(self.klinesDf.close, period=15).df
        elif self.indicator == 'SMA':
            self.klinesDf['12sma'] = btalib.sma(self.klinesDf.close, period=12).df
            self.klinesDf['50sma'] = btalib.sma(self.klinesDf.close, period=50).df
        elif self.indicator == 'MACD':
            self.klinesDf['macd'],self.klinesDf['macdSignal'],self.klinesDf['macdHist'] = btalib.macd(self.klinesDf.close, pfast=12, pslow=26, psignal=9)
        else:
            return None

    def calculateStrategy(self):
        if self.indicator == 'MACD' and self.strategy == 'CROSSOVER':
            crosses = []
            greaterMacd = False
            for i in range(len(self.klinesDf.macd)):
                # If both MACD and MACDSignal are not NaN
                if not np.isnan(self.klinesDf.macd[i]) and not np.isnan(self.klinesDf.macdSignal[i]):
                    # Bearish Signal
                    if self.klinesDf.macd[i] > self.klinesDf.macdSignal[i] and not greaterMacd:
                        cross = [self.klinesDf.index[i], self.klinesDf.macd[i], 'BUY', self.klinesDf.close[i]]
                        greaterMacd = True
                    # Bullish Signal
                    elif self.klinesDf.macd[i] <= self.klinesDf.macdSignal[i] and greaterMacd:
                        cross = [self.klinesDf.index[i], self.klinesDf.macd[i], 'SELL', self.klinesDf.close[i]]
                        greaterMacd = False
                    else:
                        continue
                    crosses.append(cross)
            return np.array(crosses)
        elif self.indicator == 'RSI' and self.strategy == 'OVERBOUGHT':
            operations = []
            for i in range(len(self.klinesDf.rsi)):
                if not np.isnan(self.klinesDf.rsi[i]):
                    # RSI over 70, overbought
                    if self.klinesDf.rsi[i] > 70:
                        operation = [self.klinesDf.index[i], self.klinesDf.rsi[i], 'SELL', self.klinesDf.close[i]]
                    # RSI below 30, oversold
                    elif self.klinesDf.rsi[i] < 30:
                        operation = [self.klinesDf.index[i], self.klinesDf.rsi[i], 'BUY', self.klinesDf.close[i]]
                    else:
                        continue
                    operations.append(operation)
            return np.array(operations)
        elif self.indicator == 'SMA' and self.strategy == 'CROSSOVER':
            crosses = []
            greaterSma12 = False
            for i in range(len(self.klinesDf['12sma'])):
                # If both 12sma and 20sma are not NaN
                if not np.isnan(self.klinesDf['12sma'][i]) and not np.isnan(self.klinesDf['50sma'][i]):
                    # Bearish signal
                    if self.klinesDf['12sma'][i] > self.klinesDf['50sma'][i] and not greaterSma12:
                        cross = [self.klinesDf.index[i], self.klinesDf['12sma'][i], 'BUY', self.klinesDf.close[i]]
                        greaterSma12 = True
                    # Bullish signal
                    elif self.klinesDf['12sma'][i] <= self.klinesDf['50sma'][i] and greaterSma12:
                        cross = [self.klinesDf.index[i], self.klinesDf['12sma'][i], 'SELL', self.klinesDf.close[i]]
                        greaterSma12 = False
                    else:
                        continue
                    crosses.append(cross)
            return np.array(crosses)
        
    def plotIndicator(self):
        plt.style.use('dark_background')
        plt.title(self.indicator + " Plot for " + self.tradePair + " on " + self.tradeInterval)
        plt.xlabel("Open Time")
        plt.ylabel("Value")
        if self.indicator == 'MACD':
            plt.plot(self.klinesDf.index, self.klinesDf.macd, label='MACD')
            plt.plot(self.klinesDf.index, self.klinesDf.macdSignal, label='MACD Signal')
            plt.plot(self.klinesDf.index, self.klinesDf.macdHist, label='MACD Histogram')
            for cross in self.strategyResult:
                plt.plot(cross[0], cross[1], ('go' if cross[2]=='BUY' else 'ro'))            
            plt.legend()
            plt.show()
        elif self.indicator == 'RSI':
            plt.plot(self.klinesDf.index, self.klinesDf.rsi, label='RSI')
            plt.axhline(y=70, xmin=0, xmax=1,color='r',linestyle='--',label='Overbought')
            plt.axhline(y=30, xmin=0, xmax=1,color='g',linestyle='--',label='Oversold')
            plt.legend()
            plt.show()
        elif self.indicator == 'SMA':
            plt.plot(self.klinesDf.index, self.klinesDf['12sma'], label='12 SMA')
            plt.plot(self.klinesDf.index, self.klinesDf['50sma'], label='50 SMA')
            for cross in self.strategyResult:
                plt.plot(cross[0], cross[1], ('go' if cross[2]=='BUY' else 'ro'))
            plt.legend()
            plt.show()
