from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from binance.enums import *
from math import log10
import userdata


class User:
    '''
    Instantiates user using API keys on userdata.py
    '''
    def __init__(self):
        self.client = self.create_client()
    
    '''
    Create binance client
    '''
    def create_client(self):
        # Read keys from userdata.py
        client =  Client(userdata.api_public, userdata.api_secret)
        # Uncomment following line to test on testnet
        # NOTE: Testnet requires different API keys
        # client.API_URL = "https://testnet.binance.vision/api"
        return client

    '''
    Reset binance client to avoid timeouts
    '''
    def reset_client(self):
        self.client = self.create_client()

    '''
    Returns users balance for assets in given trade pair
    '''
    def get_balance(self, pair):
        # Get symbol info to determine base and quote assets
        symbol_info = self.client.get_symbol_info(pair)
        # Get user's balance on base asset
        base = self.client.get_asset_balance(symbol_info['baseAsset'])
        # If no base asset owned, create dict with 0 values
        if base == None:
            base = {'asset':symbol_info['baseAsset'], 'free':0, 'locked':0}
        # Get user's balance on quote asset
        quote = self.client.get_asset_balance(symbol_info['quoteAsset'])
        # If no quote asset owned, create dict with 0 values
        if quote == None:
            quote = {'asset':symbol_info['quoteAsset'], 'free':0, 'locked':0}
        return {'base':base, 'quote':quote}

    '''
    Place market buy order for given percentage of maximum possible amount
    '''
    def buy_market(self, pair, percentage):
        # Calculate quantity to be bought of quote asset
        precision = -1*int(log10(float(self.client.get_symbol_info(pair)['filters'][0]['tickSize'])))
        # Get balance on quote asset
        quote_balance = float(self.get_balance(pair)['quote']['free'])
        qt = round(quote_balance*percentage/100, precision)
        # Check if calculated quantity is greater than minimum allowed
        if qt < float(self.client.get_symbol_info('ETHUSDT')['filters'][3]['minNotional']):
            print('Insufficient balance')
            return False
        # Constant topup values set for trading in BUSD 10-200 range
        self.topup_bnb(0.004, 0.003, self.get_balance(pair)['quote']['asset'])
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
    def sell_market(self, pair, percentage):
        # Calculate quantity to be sold of base asset
        avg_price = float(self.client.get_avg_price(pair)['price'])
        precision = -1*int(log10(float(self.client.get_symbol_info(pair)['filters'][2]['stepSize'])))
        base_balance = float(self.get_balance(pair)['base']['free'])
        qt = round(base_balance*percentage/100, precision)
        # Check if calculated quantity is greater than minimum allowed
        if qt*avg_price < float(self.client.get_symbol_info('ETHUSDT')['filters'][3]['minNotional']):
            print('Insufficient balance')
            return False
        # Constant topup values set for trading in BUSD 10-200 range
        self.topup_bnb(0.004, 0.003, self.get_balance(pair)['quote']['asset'])
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
    def topup_bnb(self, min_balance, topup, symbol):
        # Get BNB-quote pair balance
        bnb = float(self.get_balance('BNB'+symbol)['base']['free'])
        # If balance is lower than specified amount, buy with quantity topup
        if bnb < min_balance:
            qty = round(topup - bnb, 5)
            order = self.client.order_market_buy(symbol='BNB'+symbol, quantity=qty)
            print('BUY',qty,'BNB','to topup')
            return order
        return False
