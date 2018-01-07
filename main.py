# coding: utf-8
import os
from zaifapi import ZaifPublicStreamApi


#KEY = os.environ.get('ZAIF_KEY') or 'YOUR_KEY'
#SECRET = os.environ.get('ZAIF_SECRET') or 'YOUR_SECRET'
TARGET_CURRENCY_PAIR = 'btc_jpy'


class TradeHistory:

    def __init__(self):
        self.trade_history = []

    def add_history(self, trade_data):
        """

        :param TradeData trade_data:
        :return:
        """
        self.trade_history.append(trade_data)
        if len(self.trade_history) > 100:
            self.trade_history = self.trade_history[-100:]

    def up_or_down(self, other_trade_data, check_type='trade'):
        """

        :param TradeData other_trade_data:
        :param str check_type:
        :return:
        """
        if not self.trade_history:
            return 'N/A'
        difference = 0
        if check_type == 'trade':
            difference = self.get_trade_difference(other_trade_data)
        elif check_type == 'depth':
            difference = self.get_depth_difference(other_trade_data)

        if difference == 0:
            return 'STY'
        if difference > 0:
            return 'UP.'
        if difference < 0:
            return 'DWN'

    def get_trade_difference(self, other_trade_data):
        """

        :param TradeData other_trade_data:
        :return:
        """
        if not self.trade_history:
            return 0

        last_history = self.trade_history[-1]
        return round(other_trade_data.get_whole_trade_avg() - last_history.get_whole_trade_avg(), 2)

    def get_depth_difference(self, other_trade_data):
        """

        :param TradeData other_trade_data:
        :return:
        """
        if not self.trade_history:
            return 0

        last_history = self.trade_history[-1]
        return round(other_trade_data.get_whole_depth_avg() - last_history.get_whole_depth_avg(), 2)

    def get_last_price_difference(self, other_trade_data):
        """

        :param TradeData other_trade_data:
        :return:
        """
        if not self.trade_history:
            return 0

        last_history = self.trade_history[-1]
        return other_trade_data.last_price - last_history.last_price


class TradeData:

    def __init__(self, time_str, last_price, trades, asks, bids):
        self.time_str = time_str
        self.last_price = last_price
        self.trades = trades
        self.asks = asks
        self.bids = bids

        bid_data = self._get_calculated_trades('bid')
        self.bid_amount = bid_data['amount']
        self.bid_max_price = bid_data['max_price']
        self.bid_min_price = bid_data['min_price']
        self.bid_avg_price = bid_data['avg_price']

        ask_data = self._get_calculated_trades('ask')
        self.ask_amount = ask_data['amount']
        self.ask_max_price = ask_data['max_price']
        self.ask_min_price = ask_data['min_price']
        self.ask_avg_price = ask_data['avg_price']

        self.depth_ask_amount, self.depth_ask_avg = self._get_calculated_depth('ask')
        self.depth_bid_amount, self.depth_bid_avg = self._get_calculated_depth('bid')

    def _get_calculated_trades(self, trade_type):
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

    def _get_calculated_depth(self, board_type):
        target_data = None
        if board_type == 'ask':
            target_data = self.asks
        if board_type == 'bid':
            target_data = self.bids
        trade_amount = sum([tr[1] for tr in target_data])
        trade_total = sum([tr[0] * tr[1] for tr in target_data])
        return trade_amount, round(trade_total/trade_amount, 3)

    def get_whole_trade_avg(self):
        total_price = self.bid_avg_price * self.bid_amount + self.ask_avg_price * self.ask_amount
        return round(total_price / (self.ask_amount + self.bid_amount), 3)

    def get_whole_depth_avg(self):
        total_price = self.depth_ask_avg * self.depth_ask_amount + self.depth_bid_avg * self.depth_bid_amount
        return round(total_price / (self.depth_ask_amount + self.depth_bid_amount), 3)


def main():
    """
    I AM MAIN.
    :return:
    """
    zaif_stream = ZaifPublicStreamApi()
    trade_history = TradeHistory()
    try:
        # StreamAPIはジェネレータを戻しているのでこれでずっといける
        for stream in zaif_stream.execute(currency_pair=TARGET_CURRENCY_PAIR):
            time_str = stream['timestamp']
            last_prince = stream['last_price']['price']
            trades = stream['trades']
            asks = stream['asks']
            bids = stream['bids']

            trade_data = TradeData(time_str, last_prince, trades, asks, bids)
            print(
                time_str,
                trade_history.get_trade_difference(trade_data),
                trade_history.get_depth_difference(trade_data),
                trade_history.get_last_price_difference(trade_data),
                last_prince,
                trade_data.ask_avg_price,
                trade_data.bid_avg_price
            )
            trade_history.add_history(trade_data)
    except KeyboardInterrupt:
        print('Bye')


if __name__ == '__main__':
    main()
