# coding: utf-8
import datetime
from zaifapi import ZaifPublicStreamApi

TARGET_CURRENCY_PAIR = 'btc_jpy'


class TradeHistory:

    def __init__(self, history_limit_count=1000):
        self.trade_history = []
        self.history_limit_count = history_limit_count

    def add_history(self, trade_data):
        """

        :param TradeData trade_data:
        :return:
        """
        self.trade_history.append(trade_data)
        if len(self.trade_history) > self.history_limit_count:
            self.trade_history = self.trade_history[-self.history_limit_count:]

    def get_trade_difference(self, other_trade_data):
        """
        トレード情報の平均価格の変化量を取得
        :param TradeData other_trade_data:
        :return:
        """
        if not self.trade_history:
            return 0

        last_history = self.trade_history[-1]
        return round(other_trade_data.get_whole_trade_avg() - last_history.get_whole_trade_avg(), 2)

    def get_depth_difference(self, other_trade_data):
        """
        板情報の平均価格の変化量を取得
        :param TradeData other_trade_data:
        :return:
        """
        if not self.trade_history:
            return 0

        last_history = self.trade_history[-1]
        return round(other_trade_data.get_whole_depth_avg() - last_history.get_whole_depth_avg(), 2)

    def get_last_price_difference(self, other_trade_data):
        """
        終値の変化量を取得
        :param TradeData other_trade_data:
        :return:
        """
        if not self.trade_history:
            return 0

        last_history = self.trade_history[-1]
        return other_trade_data.last_price - last_history.last_price


class TradeData:
    """
    ある時点での取引情報
    """

    def __init__(self, trade_time, last_price, trades, asks, bids):
        """

        :param trade_time: 情報時刻
        :param last_price: 終値
        :param list trades: 取引実績
        :param list[float float] asks: ask一覧
        :param list[float float] bids: bid一覧
        """
        self.trade_time = trade_time
        self.last_price = last_price
        self.trades = trades
        self.asks = asks
        self.bids = bids

        bid_data = self._get_calculated_trades('bid')
        self.trade_bid_amount = bid_data['amount']
        self.trade_bid_max = bid_data['max_price']
        self.trade_bid_min = bid_data['min_price']
        self.trade_bid_avg = bid_data['avg_price']

        ask_data = self._get_calculated_trades('ask')
        self.trade_ask_amount = ask_data['amount']
        self.trade_ask_max = ask_data['max_price']
        self.trade_ask_min = ask_data['min_price']
        self.trade_ask_avg = ask_data['avg_price']

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
        # 取引量が0の場合は終値をそのまま採用する
        if amount:
            avg_price = round(total / amount, 3)
            max_price = max([tr['amount'] for tr in target_list])
            min_price = min([tr['amount'] for tr in target_list])
        else:
            avg_price = self.last_price
            max_price = self.last_price
            min_price = self.last_price

        return {
            'amount': amount,
            'max_price': max_price,
            'min_price': min_price,
            'avg_price': avg_price
        }

    def _get_calculated_depth(self, board_type):
        """
        板情報をまとめて、平均価格や取引量を求める
        :param board_type:
        :return:
        """
        target_data = None
        if board_type == 'ask':
            target_data = self.asks
        if board_type == 'bid':
            target_data = self.bids
        trade_amount = sum([tr[1] for tr in target_data])
        trade_total = sum([tr[0] * tr[1] for tr in target_data])
        return trade_amount, round(trade_total/trade_amount, 3)

    def get_whole_trade_avg(self):
        """
        全トレードの平均価格
        :return:
        """
        total_price = self.trade_bid_avg * self.trade_bid_amount + self.trade_ask_avg * self.trade_ask_amount
        return round(total_price / (self.trade_ask_amount + self.trade_bid_amount), 3)

    def get_whole_depth_avg(self):
        """
        全板の平均価格
        :return:
        """
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
            trade_time = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
            last_price = stream['last_price']['price']
            trades = stream['trades']
            asks = stream['asks']
            bids = stream['bids']

            trade_data = TradeData(trade_time, last_price, trades, asks, bids)
            print(
                time_str,
                trade_history.get_trade_difference(trade_data),
                trade_history.get_depth_difference(trade_data),
                trade_history.get_last_price_difference(trade_data),
                last_price,
                trade_data.trade_ask_avg,
                trade_data.trade_bid_avg
            )
            trade_history.add_history(trade_data)
    except KeyboardInterrupt:
        print('Bye')


if __name__ == '__main__':
    main()
