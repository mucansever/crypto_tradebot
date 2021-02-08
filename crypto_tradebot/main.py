import argparse
from trade_bot import *


def parse_args():
    parser = argparse.ArgumentParser(description='Define running conditions for the bot.')
    parser.add_argument('symbol', help='Trade pair: eg. "ETHUSDT", "BTCBUSD"')
    parser.add_argument('runtime', help='Duration of the bot: eg. "4h", "30m"')
    parser.add_argument('--interval', help='Kline intervals used to calculate indicators: eg. "1m", "1d"')
    parser.add_argument('--initial_state', help='Initial state of the bot: either BUY or SELL')
    args = parser.parse_args()

    interval = '1m'
    initial_state = 'BUY'

    if args.initial_state and (args.initial_state == 'BUY' or args.initial_state == 'SELL'):
        initial_state = args.initial_state

    if args.interval:
        interval = args.interval
    
    return [args.symbol, interval, args.runtime, initial_state]

def main():
    args = parse_args()
    user = User()
    bot = TradeBot(user, args[0], args[1], args[2])
    bot.run(args[3])

if __name__ == '__main__':
    main()
