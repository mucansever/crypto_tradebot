from strategy import *

class Backtest:
    def __init__(self, startDate, endDate, balance, strategy: Strategy):
        self.startDate = startDate
        self.endDate = endDate
        self.initialBalance = balance
        self.updatedBalance = balance
        self.strategy = strategy
        self.portfolio = []
        self.successRate = 0

    def run(self):
        nextOrder = 'BUY'
        boughtAmount = 0
        totalSells = 0
        signals = self.strategy.getResult()
        for signal in signals:
            if signal[0] < self.startDate:
                continue
            if signal[0] > self.endDate:
                break

            if nextOrder == 'BUY' and signal[2] == 'BUY':
                nextOrder = 'SELL'
                self.portfolio.append([signal[3], 'BUY'])
                boughtAmount = self.updatedBalance/signal[3]
                self.updatedBalance = 0

            if nextOrder == 'SELL' and signal[2] == 'SELL':
                nextOrder = 'BUY'
                buyPrice = self.portfolio[-1][0]
                self.portfolio.append([signal[3], 'SELL'])
                self.updatedBalance = boughtAmount*signal[3]
                boughtAmount = 0
                totalSells += 1
                if signal[3] > buyPrice:
                    self.successRate += 1

        self.successRate /= totalSells
        self.updatedBalance = boughtAmount*self.portfolio[-1][0] + self.updatedBalance
        
    def results(self):
        for item in self.portfolio:
            print(item[1], item[0])
        print('Initial balance:', self.initialBalance)
        print('Final balance:', self.updatedBalance)
        print('Change in percentage:', str(self.updatedBalance/self.initialBalance*100-100) + '%')
        print('Success rate:', str(self.successRate*100)+'%')
