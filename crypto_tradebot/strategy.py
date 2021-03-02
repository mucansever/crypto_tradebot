from numpy.core.numeric import NaN
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import btalib

class Strategy:
    '''
    Strategy object takes indicator, strategy, symbol interval and kline information 
    to returns buy/sell signals and charts from indicator/strategy pair.
    '''
    def __init__(self, indicator, strategy, symbol, trade_interval, klines: pd.DataFrame):
        self.indicator = indicator
        self.strategy = strategy
        self.symbol = symbol
        self.trade_interval = trade_interval
        self.klines = klines
        self.calculate_indicator()
        self.result = self.calculate_strategy()

    '''
    Returns indicator.
    '''
    def get_indicator(self):
        return self.indicator

    '''
    Returns strategy.
    '''
    def get_strategy(self):
        return self.strategy

    '''
    Returns trade pair.
    '''
    def get_symbol(self):
        return self.symbol

    '''
    Returns kline's intervals.
    '''
    def get_trade_interval(self):
        return self.trade_interval

    '''
    Returns resulting dataframe.
    '''
    def get_dataframe(self):
        return self.klines

    '''
    Returns BUY/SELL signals for each kline in dataset.
    '''
    def get_result(self):
        return self.result

    '''
    Calculates indicator and appends them to dataframe.
    '''
    def calculate_indicator(self):
        # RSI 15 Indicator
        if self.indicator == 'RSI':
            self.klines['rsi'] = btalib.rsi(self.klines.close, period=15).df
        # SMA 12-50 Indicator
        elif self.indicator == 'SMA':
            self.klines['12sma'] = btalib.sma(self.klines.close, period=12).df
            self.klines['50sma'] = btalib.sma(self.klines.close, period=50).df
        # MACD 12-26-9 Indicator
        elif self.indicator == 'MACD':
            self.klines['macd'],self.klines['macdSignal'],self.klines['macdHist'] = btalib.macd(self.klines.close, pfast=12, pslow=26, psignal=9)
        else:
            return None

    '''
    Generates buy/sell signals from indicator results and given strategy.
    Returns a list of following list for each operation point:
    [date, indicator value, signal, closing price]
    '''
    def calculate_strategy(self):
        # MACD CROSSOVER Strategy
        # Generates signals based on macd-macdSignal lines' crossovers
        if self.indicator == 'MACD' and self.strategy == 'CROSSOVER':
            # Empty crossovers list
            crosses = []
            # Initialize macdSignal as it is below the macd line.
            macd_greater = False
            for i in range(len(self.klines.macd)):
                # Check if both MACD and MACDSignal are valid
                if not np.isnan(self.klines.macd[i]) and not np.isnan(self.klines.macdSignal[i]):
                    # Bearish Signal - BUY
                    if self.klines.macd[i] > self.klines.macdSignal[i] and not macd_greater:
                        # put crossover info into a list
                        cross = [self.klines.index[i], self.klines.macd[i], 'BUY', self.klines.close[i]]
                        # macdSignal has passed the macd line.
                        macd_greater = True
                    # Bullish Signal - SELL
                    elif self.klines.macd[i] <= self.klines.macdSignal[i] and macd_greater:
                        # put crossover info into a list
                        cross = [self.klines.index[i], self.klines.macd[i], 'SELL', self.klines.close[i]]
                        # macdSignal has dropped below the macd line.
                        macd_greater = False
                    else:
                        continue
                    # Append crossover to answer list
                    crosses.append(cross)
            return np.array(crosses)
        # RSI OVERBOUGHT Strategy
        # Generates signals from RSI indicator passing certain pivot points
        elif self.indicator == 'RSI' and self.strategy == 'OVERBOUGHT':
            # Initialize empty signals list
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
                    # Append operation to answer list
                    operations.append(operation)
            return np.array(operations)
        # SMA CROSSOVER Strategy
        # Generates signals based of 12sma's relationship with 50sma.
        elif self.indicator == 'SMA' and self.strategy == 'CROSSOVER':
            # Empty crossovers list
            crosses = []
            # Initialize 12sma as it's below 50sma
            greater_sma = False
            for i in range(len(self.klines['12sma'])):
                # If both 12sma and 50sma are valid
                if not np.isnan(self.klines['12sma'][i]) and not np.isnan(self.klines['50sma'][i]):
                    # Bearish signal - BUY
                    if self.klines['12sma'][i] > self.klines['50sma'][i] and not greater_sma:
                        cross = [self.klines.index[i], self.klines['12sma'][i], 'BUY', self.klines.close[i]]
                        # 12sma has passed 50sma
                        greater_sma = True
                    # Bullish signal - SELL
                    elif self.klines['12sma'][i] <= self.klines['50sma'][i] and greater_sma:
                        cross = [self.klines.index[i], self.klines['12sma'][i], 'SELL', self.klines.close[i]]
                        # 12sma has dropped below 50sma
                        greater_sma = False
                    else:
                        continue
                    # Append crossover to answers list
                    crosses.append(cross)
            return np.array(crosses)
    
    '''
    Plots indicator-strategy pair of object marking buy/sell points.
    This feature has not been used in actual implementation of the bot, it's mostly 
    for testing purposes of newly designed strategies.
    '''
    def plotIndicator(self):
        # Style info and labels
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
