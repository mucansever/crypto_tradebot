from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from binance.enums import *
from numpy.core.numeric import NaN
from math import log10

class User:
    '''
    Instantiates user from a file with public API key on first, secret key
    on second line
    '''
    def __init__(self, fileName):
        self.client = self.createClient(fileName)
    
    # Create binance client
    def createClient(self,fileName):
        lines = []
        with open(fileName,'r') as file:
            lines = [line.strip('\n') for line in file.readlines()]
        client =  Client(lines[0], lines[1])
        # Uncomment following line to test on testnet
        # NOTE: Testnet requires different API keys
        # client.API_URL = "https://testnet.binance.vision/api"
        return client

    '''
    Returns users balance for assets in given trade pair
    '''
    def getBalance(self, pair):
        # Get symbol info to determine base and quote assets
        symbolInfo = self.client.get_symbol_info(pair)
        # Get user's balance on base asset
        base = self.client.get_asset_balance(symbolInfo['baseAsset'])
        # If no base asset owned, create dict with 0 values
        if base == None:
            base = {'asset':symbolInfo['baseAsset'], 'free':0, 'locked':0}
        # Get user's balance on quote asset
        quote = self.client.get_asset_balance(symbolInfo['quoteAsset'])
        # If no quote asset owned, create dict with 0 values
        if quote == None:
            quote = {'asset':symbolInfo['quoteAsset'], 'free':0, 'locked':0}
        return {'base':base, 'quote':quote}

    '''
    Place market buy order for given percentage of maximum possible amount
    '''
    def buyMarket(self, pair, percentage):
        # Calculate quantity to be bought of quote asset
        precision = -1*int(log10(float(self.client.get_symbol_info(pair)['filters'][0]['tickSize'])))
        # Get balance on quote asset
        quoteBalance = float(self.getBalance(pair)['quote']['free'])
        qt = round(quoteBalance*percentage/100, precision)
        # Check if calculated quantity is greater than minimum allowed
        if qt < float(self.client.get_symbol_info('ETHUSDT')['filters'][3]['minNotional']):
            print('Insufficient balance')
            return False
        # Constant topup values set for trading in BUSD 10-200 range
        self.topup(0.004, 0.003, self.getBalance(pair)['quote']['asset'])
        try:
            return self.client.order_market_buy(symbol=pair, quoteOrderQty=qt)
        except BinanceAPIException as e:
            print(e)
        except BinanceOrderException as e:
            print(e)
        return False
        
    '''
    Place market sell order for given percentage of maximum possible amount
    '''
    def sellMarket(self, pair, percentage):
        # Calculate quantity to be sold of base asset
        avgPrice = float(self.client.get_avg_price(pair)['price'])
        precision = -1*int(log10(float(self.client.get_symbol_info(pair)['filters'][2]['stepSize'])))
        baseBalance = float(self.getBalance(pair)['base']['free'])
        qt = round(baseBalance*percentage/100, precision)
        # Check if calculated quantity is greater than minimum allowed
        if qt*avgPrice < float(self.client.get_symbol_info('ETHUSDT')['filters'][3]['minNotional']):
            print('Insufficient balance')
            return False
        # Constant topup values set for trading in BUSD 10-200 range
        self.topup(0.004, 0.003, self.getBalance(pair)['quote']['asset'])
        try:
            order =  self.client.order_market_sell(symbol=pair, quantity=qt)
            return order
        except BinanceAPIException as e:
            print(e)
        except BinanceOrderException as e:
            print(e)    
        return False

    '''
    Top-up BNB balance to pay for commission fees with lower rates
    '''
    def topup(self, minBalance, topup, symbol):
        # Get BNB-quote pair balance
        bnb = float(self.getBalance('BNB'+symbol)['base']['free'])
        # If balance is lower than specified amount, buy with quantity topup
        if bnb < minBalance:
            qty = round(topup - bnb, 5)
            order = self.client.order_market_buy(symbol='BNB'+symbol, quantity=qty)
            print(bnb)
            return order
        return False
