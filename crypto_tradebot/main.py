from trade_bot import *
from backtest import *

if __name__ == '__main__':
    user = User('acc.txt')
    bot = TradeBot(user, 'ETHUSDT', '1m', '1h')
    bot.run()
