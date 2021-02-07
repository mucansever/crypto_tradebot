from user import *
from strategy import *
from datetime import datetime, timedelta
import time
from requests import exceptions


class TradeBot:
    '''
    User object needs to be created beforehand
    '''
    def __init__(self, user: User, tradePair, tradeInterval, runtime):
        # User object containing client
        self.user = user
        # Trading pair eg.'BTCUSDT', 'ETHBUSD'
        self.tradePair = tradePair
        # Trading interval eg.'1m', '1d'
        self.tradeInterval = tradeInterval
        self.runtime = self.calculateRuntime(runtime)

    '''
    Converts given time in formats like '1m', '2h' to timedelta
    '''
    def calculateRuntime(self, runtime):
        if runtime[-1] == 's':
            return timedelta(seconds=int(runtime[:-1]))
        elif runtime[-1] == 'm':
            return timedelta(minutes=int(runtime[:-1]))
        elif runtime[-1] == 'h':
            return timedelta(hours=int(runtime[:-1]))

    '''
    Returns a pandas dataframe of klines
    '''
    def createDataframe(self):
        # Gets klines, I3 indicators may return wrong results with low limits
        klines = self.user.client.get_klines(symbol=self.tradePair,interval=self.tradeInterval,limit=300)
        for line in klines:
            for i in range(5):
                line[i] = float(line[i])
            del line[5:]
        df = pd.DataFrame(klines,columns=['date','open','high','low','close'])
        df.set_index('date',inplace=True)
        df.index = pd.to_datetime(df.index, unit='ms')
        return df

    '''
    Graphs given indicator
    Current indicators: 'MACD', 'RSI', 'SMA
    '''
    def graph(self, indicator):
        klines = self.createDataframe()
        if indicator == 'MACD':
            st = Strategy('MACD','CROSSOVER',self.tradePair,self.tradeInterval,klines)
        elif indicator == 'SMA':
            st = Strategy('SMA','CROSSOVER',self.tradePair,self.tradeInterval,klines)
        elif indicator == 'RSI':
            st = Strategy('RSI','OVERBOUGHT',self.tradePair,self.tradeInterval,klines)
        else:
            return False
        st.plotIndicator()

    '''
    Runs trade bot which only has one state(BUY or SELL) at a time. 
    Initial state can be given as a parameter.
    '''
    def run(self, startWith='BUY'):
        print("Trades begin")
        startTime = datetime.utcnow()
        # Terminate when given time is reached
        while (self.runtime > datetime.utcnow() - startTime):
            try:
                # Create dataframe and fill MACD, RSI columns
                klines = self.createDataframe()
                macd = Strategy('MACD','CROSSOVER',self.tradePair,self.tradeInterval,klines)
                rsi = Strategy('RSI','OVERBOUGHT',self.tradePair,self.tradeInterval,klines)
                # Macd indicator to determine to buy or sell
                macdSignal = 'HOLD'
                # Operation to perform next (either BUY or SELL)
                nextOperation = startWith
                # Rsi value for last kline
                rsiValue = rsi.getResult()[-1][1]

                # Make sure timestamps match
                if macd.getResult()[-1][0] == klines.index[-1]: 
                    macdSignal = macd.getResult()[-1][2]
                else:
                    macdSignal = 'HOLD'
                
                # Perform the trade or don't based on macdSignal
                # Amount to be traded is determined by the RSI indicator
                # Above 70 and below 30 are considered as the low-risk zones
                if nextOperation == macdSignal:
                    order = False
                    if nextOperation == 'BUY':
                        if rsiValue <= 30:
                            order = self.user.buyMarket(self.tradePair, 70)
                            nextOperation = 'SELL'
                        elif rsiValue <= 50:
                            order = self.user.buyMarket(self.tradePair, 30)
                            nextOperation = 'SELL'
                    elif nextOperation == 'SELL':
                        if rsiValue >= 70:
                            order = self.user.sellMarket(self.tradePair, 100)
                            nextOperation = 'BUY'
                        elif rsiValue >= 50:
                            order = self.user.sellMarket(self.tradePair, 50)
                            nextOperation = 'BUY'   
                    if order != False:
                        self.showMessage(order)
            # Handles requests' read operation timeouts
            except exceptions.ReadTimeout:
                print('Read timeout')
            # Sleep in order to avoid timeouts
            time.sleep(10)

    '''
    Shows information about the trade performed
    '''
    def showMessage(self, order):
        if order == False:
            print('Error: trade did not occur')
        else:
            print('Position after trade:')
            print(self.user.getBalance(self.tradePair)['base'])
            print(self.user.getBalance(self.tradePair)['quote'])
