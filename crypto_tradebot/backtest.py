from strategy import Strategy

class Backtest:
    '''
    Backtest given strategy using historical data with specified start and end dates.
    Strategy object with dataset needs to be created beforehand.
    '''
    def __init__(self, start_date, end_date, balance, strategy: Strategy):
        self.start_date = start_date
        self.end_date = end_date
        self.initial_balance = balance
        self.updated_balance = balance
        self.strategy = strategy
        self.portfolio = []
        self.success_rate = 0

    '''
    Run the backtest. 
    Starts from BUY state and buys/sells at the first signal, repeats this 
    process for all data in dataset.
    '''
    def run(self):
        next_order = 'BUY'
        bought_amount = 0
        totalSells = 0
        signals = self.strategy.getResult()
        for signal in signals:
            if signal[0] < self.start_date:
                continue
            if signal[0] > self.end_date:
                break

            if next_order == 'BUY' and signal[2] == 'BUY':
                next_order = 'SELL'
                self.portfolio.append([signal[3], 'BUY'])
                bought_amount = self.updated_balance/signal[3]
                self.updated_balance = 0

            if next_order == 'SELL' and signal[2] == 'SELL':
                next_order = 'BUY'
                buy_price = self.portfolio[-1][0]
                self.portfolio.append([signal[3], 'SELL'])
                self.updated_balance = bought_amount*signal[3]
                bought_amount = 0
                totalSells += 1
                if signal[3] > buy_price:
                    self.success_rate += 1

        self.success_rate /= totalSells
        self.updated_balance = bought_amount*self.portfolio[-1][0] + self.updated_balance
        
    '''
    Print final results of the backtesting.
    Must be used after .run()
    '''
    def results(self):
        for item in self.portfolio:
            print(item[1], item[0])
        print('Initial balance:', self.initial_balance)
        print('Final balance:', self.updated_balance)
        print('Change in percentage:', str(self.updated_balance/self.initial_balance*100-100) + '%')
        print('Success rate:', str(self.success_rate*100)+'%')
