import urllib
import json
import time
import hmac,hashlib
import requests
import urllib.parse

def createTimeStamp(datestr, format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(datestr, format))

api_key = "KEY HERE"
api_secret = "SECRET HERE"

class poloniex:
    base_comand_url = 'https://poloniex.com/public?command='
    private_command_url = 'https://poloniex.com/tradingApi'
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret
        self._open()
    def _open(self):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0"
    def _close(self):
        self.session.close()
    def _get(self,url):
        tmp = self.session.get(url)
        if tmp.status_code not in (200, 201, 202,502):
            tmp.raise_for_status()
        return json.loads(tmp.content.decode())
    def _post(self,url,data,headers):
        tmp = self.session.post(url, data = data, headers = headers)
        if tmp.status_code not in (200, 201, 202,502):
            tmp.raise_for_status()
        return json.loads(tmp.content.decode())
    def post_process(self, before):
        after = before

        # Add timestamps if there isnt one but is a datetime
        if 'return' in after:
            if isinstance(after['return'], list):
                for x in range(len(after['return'])):
                    if isinstance(after['return'][x], dict):
                        if 'datetime' in after['return'][x] and 'timestamp' not in after['return'][x]:
                            after['return'][x]['timestamp'] = float(createTimeStamp(after['return'][x]['datetime']))
                            
        return after

    def api_query(self, command, req={}):

        if command == "returnTicker" or command == "return24hVolume":
            return self._get(self.base_comand_url+command)
        elif command == "returnOrderBook":
            return self._get(self.base_comand_url+command + '&currencyPair=' + str(req['currencyPair']))
        elif command == "returnMarketTradeHistory":
            return self._get(self.base_comand_url+ "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair']))
        else:
            req['command'] = command
            req['nonce'] = int(time.time()*1000)
            
            post_data = urllib.parse.urlencode(req,quote_via=urllib.parse.quote_plus).encode()
            sign = hmac.new(self.Secret.encode(), post_data, hashlib.sha512).hexdigest()
            headers = {
                'Sign': sign,
                'Key': self.APIKey
            }
            return self.post_process(self._post(self.private_command_url,req,headers))

    def returnTicker(self):
        return self.api_query("returnTicker")

    def return24Volume(self):
        return self.api_query("return24hVolume")

    def returnOrderBook (self, currencyPair):
        return self.api_query("returnOrderBook", {'currencyPair': currencyPair})

    def returnMarketTradeHistory (self, currencyPair):
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currencyPair})


    # Returns all of your balances.
    # Outputs: 
    # {"BTC":"0.59098578","LTC":"3.31117268", ... }
    def returnBalances(self):
        return self.api_query('returnBalances')

    # Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs: 
    # orderNumber   The order number
    # type          sell or buy
    # rate          Price the order is selling or buying at
    # Amount        Quantity of order
    # total         Total value of order (price * quantity)
    def returnOpenOrders(self,currencyPair="all"):
        return self.api_query('returnOpenOrders',{"currencyPair":currencyPair})


    # Returns your trade history for a given market, specified by the "currencyPair" POST parameter
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs: 
    # date          Date in the form: "2014-02-19 03:44:59"
    # rate          Price the order is selling or buying at
    # amount        Quantity of order
    # total         Total value of order (price * quantity)
    # type          sell or buy
    def returnTradeHistory(self,currencyPair):
        return self.api_query('returnTradeHistory',{"currencyPair":currencyPair})

    # Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is buying at
    # amount        Amount of coins to buy
    # Outputs: 
    # orderNumber   The order number
    def buy(self,currencyPair,rate,amount,fillOrKill=0):
        return self.api_query('buy',{"currencyPair":currencyPair,"rate":rate,"amount":amount,"fillOrKill":fillOrKill})

    # Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is selling at
    # amount        Amount of coins to sell
    # Outputs: 
    # orderNumber   The order number
    def sell(self,currencyPair,rate,amount,fillOrKill=0):
        return self.api_query('sell',{"currencyPair":currencyPair,"rate":rate,"amount":amount,"fillOrKill":fillOrKill})
    def moveOrder(self,orderNumber,rate,amount):
        return self.api_query('moveOrder',{"orderNumber":orderNumber,"rate":rate,"amount":amount})
    def returnAvailableAccountBalances(self):
        return self.api_query('returnAvailableAccountBalances',{"account":"exchange"})
    # Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
    # Inputs:
    # currencyPair  The curreny pair
    # orderNumber   The order number to cancel
    # Outputs: 
    # succes        1 or 0
    def cancel(self,orderNumber):
        return self.api_query('cancelOrder',{"orderNumber":orderNumber})
    # Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method, the withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount", and "address". Sample output: {"response":"Withdrew 2398 NXT."} 
    # Inputs:
    # currency      The currency to withdraw
    # amount        The amount of this coin to withdraw
    # address       The withdrawal address
    # Outputs: 
    # response      Text containing message about the withdrawal
    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw',{"currency":currency, "amount":amount, "address":address})
if __name__=="__main__":
    p = poloniex(api_key,api_secret)
