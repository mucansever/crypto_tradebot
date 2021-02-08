from user import User
from strategy import Strategy
import pandas as pd
from datetime import datetime, timedelta
import time
from requests import exceptions


class TradeBot:
    '''
    User object needs to be created beforehand
    '''
    def __init__(self, user: User, symbol, trade_interval, runtime):
        # User object containing client
        self.user = user
        # Trading pair eg.'BTCUSDT', 'ETHBUSD'
        self.symbol = symbol
        # Trading interval eg.'1m', '1d'
        self.trade_interval = trade_interval
        # Runtime eg.'15m', '4h'
        self.runtime = self.calculate_timedelta(runtime)

    '''
    Converts given time in formats like '1m', '2h' to timedelta
    '''
    def calculate_timedelta(self, runtime):
        if runtime[-1] == 's':
            return timedelta(seconds=float(runtime[:-1]))
        elif runtime[-1] == 'm':
            return timedelta(minutes=float(runtime[:-1]))
        elif runtime[-1] == 'h':
            return timedelta(hours=float(runtime[:-1]))

    '''
    Returns a pandas dataframe of klines
    '''
    def create_dataframe(self):
        # Gets klines, I3 indicators may be wrong results with low limits
        klines = self.user.client.get_klines(symbol=self.symbol,interval=self.trade_interval,limit=300)
        # Remove unnecessary columns
        for line in klines:
            for i in range(5):
                line[i] = float(line[i])
            del line[5:]
        df = pd.DataFrame(klines,columns=['date','open','high','low','close'])
        # Set date column as index
        df.set_index('date', inplace=True)
        df.index = pd.to_datetime(df.index, unit='ms')
        return df

    '''
    Graphs given indicator
    Current indicators: 'MACD', 'RSI', 'SMA'
    '''
    def plot(self, indicator):
        klines = self.create_dataframe()
        if indicator == 'MACD':
            st = Strategy('MACD','CROSSOVER',self.symbol,self.trade_interval,klines)
        elif indicator == 'SMA':
            st = Strategy('SMA','CROSSOVER',self.symbol,self.trade_interval,klines)
        elif indicator == 'RSI':
            st = Strategy('RSI','OVERBOUGHT',self.symbol,self.trade_interval,klines)
        else:
            return False
        st.plotIndicator()

    '''
    Runs trade bot which only has one state(BUY or SELL) at a time. 
    Initial state can be given as a parameter.
    '''
    def run(self, startWith='BUY'):
        print("Trades begin")
        start_time = datetime.utcnow()
        reset_interval = self.calculate_timedelta('2h')
        uptime = datetime.utcnow() - start_time
        # Terminate when given time is reached
        while (self.runtime > datetime.utcnow() - start_time):
            try:
                # Reset the client every 2 hours
                if uptime > reset_interval:
                    self.user.reset_client()
                    uptime -= reset_interval
                    
                # Create dataframe and fill MACD, RSI columns
                klines = self.create_dataframe()
                macd = Strategy('MACD','CROSSOVER',self.symbol,self.trade_interval,klines)
                rsi = Strategy('RSI','OVERBOUGHT',self.symbol,self.trade_interval,klines)
                # Macd indicator to determine to buy or sell
                macd_signal = 'HOLD'
                # Operation to perform next (either BUY or SELL)
                next_operation = startWith
                # Rsi value for last kline
                rsi_indicator = rsi.get_result()[-1][1]
                # Make sure timestamps match
                if macd.get_result()[-1][0] == klines.index[-1]: 
                    macd_signal = macd.get_result()[-1][2]
                else:
                    macd_signal = 'HOLD'
                
                # Perform the trade or don't based on macd_signal
                # Amount to be traded is determined by the RSI indicator
                # Above 70 and below 30 are considered as the low-risk zones
                if next_operation == macd_signal:
                    order = False
                    if next_operation == 'BUY':
                        if rsi_indicator <= 30:
                            order = self.user.buy_market(self.symbol, 70)
                            next_operation = 'SELL'
                        elif rsi_indicator <= 50:
                            order = self.user.buy_market(self.symbol, 30)
                            next_operation = 'SELL'
                    elif next_operation == 'SELL':
                        if rsi_indicator >= 70:
                            order = self.user.sell_market(self.symbol, 100)
                            next_operation = 'BUY'
                        elif rsi_indicator >= 50:
                            order = self.user.sell_market(self.symbol, 50)
                            next_operation = 'BUY'   
                    if order != False:
                        self.showMessage(order)
            # Handles requests' read operation timeouts
            except exceptions.ReadTimeout:
                print('Read timeout')
            # Sleep in order to avoid timeouts
            time.sleep(15)

    '''
    Shows information about the trade performed
    '''
    def showMessage(self, order):
        if order == False:
            print('Error: trade did not occur')
        else:
            print('Position after trade:')
            base = self.user.get_balance(self.symbol)['base']
            quote = self.user.get_balance(self.symbol)['quote']
            print(base['asset'],'Free:',base['free'],'Locked:',base['locked'])
            print(quote['asset'],'Free:',quote['free'],'Locked:',quote['locked'])
