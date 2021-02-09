# crypto_tradebot
A crypto trading bot that runs on Binance
## Implementation
This bot has only one state, either buy or sell, at a time which changes between the two repeatedly. When to buy or sell is determined by the bearish and bullish signals acquired from MACD-MACDsignal line crossovers and how much to buy or sell is determined via the RSI indicator.
## Dependencies
Python 3.7 or above is needed. Required modules can be easily installed via pip as follows:
```
pip install -r requirements.txt
```
You'll also need a set of binance API keys and update userdata.py with those respectively. If you don't have one already, steps on following article can be followed: https://www.binance.com/en/support/faq/360002502072-How-to-create-API
## Usage
```
python3 main.py <symbol> <runtime> --interval [OPTIONAL] --initial_state [OPTIONAL]
```
Symbol and runtime arguments are mandatory while --interval and --initial_state are optional. 
- Symbol argument is a basic trade pair string such as 'ETHUSDT' or 'BTCBNB'. Pairs are limited woth the ones Binance API allows.
- Runtime argument is for how long the bot should run with the format a number followed by either 's'(second), 'm'(minute) or 'h'(hour) such as '4h'.
- Interval argument is the interval of klines, its format is same as runtime.
- Initial state argument is either 'BUY' or 'SELL', specifying the first operation to be performed.
## Note
Because of the trade limits on Binance API, given account must have at least $20 USD to use the bot on cryptocurrencies such as ETH and BTC. \
The logic behind strategies used on this bot can be read from following articles:
- https://www.ig.com/en/trading-strategies/macd-trading-strategy-190610
- https://medium.com/@sol_98230/rsi-5-basic-strategies-4-steps-how-to-connect-it-to-the-trading-bot-a2aa5bb70f6c
## Future Improvements
- 'strategy.py' to be reorganized. 
- Better error handling. 
- Plotting indicators on runtime.
