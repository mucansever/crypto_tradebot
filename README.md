# Crypto Tradebot
A crypto trading bot that runs on Binance
## Install dependencies
```
pip install -r requirements.txt
```
## How to run
Update API key information on userdata.py
```
python3 main.py <symbol> <runtime> --interval [OPTIONAL] --initial_state [OPTIONAL]
```
## How it works
The bot has one state(either buy or sell) at a time which changes between the two repeatedly. When to buy/sell is determined by bearish and bullish signals acquired from MACD-MACDsignal line crossovers and how much to buy/sell is determined using the RSI indicator.
