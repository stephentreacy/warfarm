from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from dotenv import load_dotenv
from datetime import datetime, timezone
import warfarm as wf
import pandas as pd
import os
import pymongo
import time

app = Flask(__name__)
api = Api(app)
load_dotenv()

client_db = pymongo.MongoClient()
warfarm_db = client_db['warfarm_db']
saved_items = warfarm_db['saved_items']

class ItemPrices(Resource):
    def get(self):
        items = wf.get_item_list(request.values['link'])
        current_time = datetime.now()

        item_orders = {}

        for item in items:
            #Check database first for recent items
            saved_item = saved_items.find_one({'item':item})

            #If last API request was within the last hour, use database values, otherwise update from warframe.market
            if (current_time-saved_item['updated']).seconds < 3600:
                buy_orders = saved_item['buy_orders']
                sell_orders = saved_item['sell_orders']  
            else:
                orders = wf.get_market_prices(item, 'item')
                                
                if orders:
                    df_orders = pd.json_normalize(orders['orders'])
                    df_sell = df_orders[(df_orders['user.status'] == 'ingame') & (df_orders['order_type'] == 'sell')]
                    df_buy = df_orders[(df_orders['user.status'] == 'ingame') & (df_orders['order_type'] == 'buy')]
                    sell_orders = df_sell.nsmallest(5, 'platinum')['platinum'].values.tolist()
                    sell_orders = ', '.join(str(int(order)) for order in sell_orders) if sell_orders else 'No Orders'
                    buy_orders = df_buy.nlargest(5, 'platinum')['platinum'].values.tolist()
                    buy_orders = ', '.join(str(int(order)) for order in buy_orders) if buy_orders else 'No Orders'

                    saved_items.update_one(dict(item=item), {'$set':{'buy_orders':buy_orders,'sell_orders':sell_orders,'updated':current_time}},upsert=True)
                
                #Wait between items to keep within 3 API requests per second
                time.sleep(0.35)
                
            item_orders[item] = {'buy_orders':buy_orders,'sell_orders':sell_orders}

        return jsonify({'data':item_orders})
    
api.add_resource(ItemPrices, '/items')

if __name__ == '__main__':
    app.run(debug=True)