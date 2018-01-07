# coding: utf-8
import time
import os
from statistics import  mean, median,variance,stdev
from zaifapi import ZaifTradeApi, ZaifPublicStreamApi
from pprint import pprint


KEY = os.environ.get('ZAIF_KEY') or 'YOUR_KEY'
SECRET = os.environ.get('ZAIF_SECRET') or 'YOUR_SECRET'
TARGET_CURRENCY_PAIR = 'btc_jpy'


class TradeData:

    def __init__(self, time_str, last_price, trades):
        self.time_str = time_str
        self.last_price = last_price
        self.trades = trades

        bid_data = self._get_calculate_trades('bid')
        self.bid_amount = bid_data['amount']
        self.bid_max_price = bid_data['max_price']
        self.bid_min_price = bid_data['min_price']
        self.bid_avg_price = bid_data['avg_price']

        ask_data = self._get_calculate_trades('bid')
        self.ask_amount = ask_data['amount']
        self.ask_max_price = ask_data['max_price']
        self.ask_min_price = ask_data['min_price']
        self.ask_avg_price = ask_data['avg_price']

    def _get_calculate_trades(self, trade_type):
        """
        トレード情報をまとめて、平均価格や取引量を求める
        :param trade_type:
        :return:
        """
        target_list = [tr for tr in self.trades if tr['trade_type'] == trade_type]

        total = sum([tr['price'] * tr['amount'] for tr in target_list])
        amount = sum([tr['amount'] for tr in target_list])
        avg_price = round(total / amount, 3)
        max_price = max([tr['amount'] for tr in target_list])
        min_price = min([tr['amount'] for tr in target_list])
        return {
            'amount': amount,
            'max_price': max_price,
            'min_price': min_price,
            'avg_price': avg_price
        }


# TODO
def trade():

    zaif_trade = ZaifTradeApi(KEY, SECRET)
    pprint(zaif_trade.get_info())
    #pprint(zaif_trade.trade(currency_pair="btc_jpy", action="ask", price=121800, amount=0.0001))
    pprint(zaif_trade.trade(currency_pair=TARGET_CURRENCY_PAIR, action="bid", price=121800, amount=0.0001))


def main():
    """
    I AM MAIN.
    :return:
    """
    zaif_stream = ZaifPublicStreamApi()
    history = []
    # StreamAPIはジェネレータを戻しているのでこれでずっといける
    for stream in zaif_stream.execute(currency_pair=TARGET_CURRENCY_PAIR):
        time_str = stream['timestamp']
        last_prince = stream['last_price']['price']
        trades = stream['trades']
        trade_data = TradeData(time_str, last_prince, trades)
        print(time_str, last_prince, trade_data.ask_avg_price, trade_data.bid_avg_price)
        history.append(trade_data)

        if len(history) > 100:
            history = history[-100:]


if __name__ == '__main__':
    main()
