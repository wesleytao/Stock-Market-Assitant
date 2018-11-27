from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet
from db import db_connect


class StockAPI(object):
    def __init__(self):
        self.engine = db_connect()
        print("connected to db...")

    def recommend(self):
        """
        find top 5 popular stock according to the watchlist
        """
        s = """
        select S.name, COUNT(*)
        from stock S, Watchlist W
        where S.ticker = W.ticker
        group by S.ticker
        order by count(*) desc
        limit 5;
        """
        cursor = self.engine.execute(s)
        names = []
        for result in cursor:
            names.append(result['name'])
        cursor.close()
        stock_str = ", ".join(names)
        return "here is top 5 popular of stocks: {} ".format(stock_str)

    def search_stock(self, stock):
        """
        find the latest price of the stock
        """
        s = """select *
        from Tick as T join Stock as S on T.ticker = S.ticker
        where S.name ~* %s
        order by record_date desc
        limit 1
        """
        print("looking for info about {}".format(stock))
        cursor = self.engine.execute(s, (stock,))
        result = cursor.fetchone()
        if result:
            date, open_price, close_price, _, _, _, _ = result
            out_str = "the open price" + \
                " for {} at {} is {} and the close price is {}".format(stock,
                                                                   str(date),
                                                                   open_price,
                                                                   close_price)
        else:
            out_str = " In our database " + \
                      "we don't find any record about {} ".format(stock)
        cursor.close()

        return out_str


stock_api = StockAPI()


class ActionSearchStock(Action):
    """
    given a stock name or ticker name,
    provide the latest price and relevant information
    """
    def name(self):
        return 'action_search_stock'

    def run(self, dispatcher, tracker, domain):
        # dispatcher.utter_message("looking for this stock")
        stock_info = stock_api.search_stock(tracker.get_slot("stock"))
        dispatcher.utter_message("{}".format(stock_info))
        return []


class ActionSuggestStock(Action):
    def name(self):
        return 'action_suggest_stock'

    def run(self, dispatcher, tracker, domain):
        recommend_info = stock_api.recommend()
        dispatcher.utter_message(recommend_info)
        return []
