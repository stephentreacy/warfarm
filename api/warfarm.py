"""Warfarm

Takes a Tenno Zone link from a file
Gets the items selected via checkboxes on website
Shows the price of the items from warframe.market"""

import time
from datetime import datetime

import requests
import pymongo
from flask import Flask, jsonify, request

def get_json(url):
    """Returns JSON from URL."""
    try:
        r = requests.get(url, verify=False)
    except:
        return {}
    else:
        json = r.json()
        return json

def all_item_ids():
    """Returns a dictionary for every item id and name."""

    items = {}
    url = 'https://tenno.zone/data'

    items_data = get_json(url)['parts']
    if not items_data: return {}

    for item in items_data:
        if any(item['name'].find(part) > -1 for part in ['Neuroptics','Chassis','Systems']): 
            item['name'] = item['name'].replace(' Blueprint','')

        items[item['id']] = item['name']

    return items

def get_items(url_id):
    """Returns the list of items from tenno.zone link.

    PARAMETERS:
        url_id - Personal ID string for tenno.zone URL"""
    
    url = 'https://tenno.zone/partlist/'+url_id

    items = get_json(url)
    all_items = all_item_ids()

    return [all_items[item] for item in items]

def get_market_prices(item):
    """Create a dictionary of orders for the item

    PARAMETERS:
        item - String of item name"""

    api_url = 'https://api.warframe.market/v1/items/'
    name_url = item.lower().replace(' ','_').replace('-','_').replace("'",'').replace('&','and')
    url_item = api_url + name_url + '/orders'

    item_json = get_json(url_item)

    return item_json['payload']['orders']


#Set up
app = Flask(__name__)
#client_db = pymongo.MongoClient()
#warfarm_db = client_db['warfarm_db']
#saved_items = warfarm_db['saved_items']

@app.route('/')
def check():
    return jsonify({'hello':'world'})

@app.route('/items')
def orders_json():
    items = get_items(request.values['link'])
    
    current_time = datetime.now()

    item_orders = {}

    for item in items:
        #Check database first for recent items
        #saved_item = saved_items.find_one({'item':item})
        saved_item = []
        #If last API request was within the last hour, use database values, otherwise update from warframe.market
        if saved_item and (current_time-saved_item['updated']).seconds < 1:
            buy_orders = saved_item['buy_orders']
            sell_orders = saved_item['sell_orders']  
        else:
            orders = get_market_prices(item)
                            
            if orders:
                buy_orders = []
                sell_orders = []

                for order in orders:
                    if order['user']['status'] == 'ingame' and order['order_type'] == 'buy':
                        buy_orders.append(order['platinum'])
                    elif order['user']['status'] == 'ingame' and order['order_type'] == 'sell':
                        sell_orders.append(order['platinum'])

                    buy_orders = sorted(buy_orders)[:5] if buy_orders else buy_orders
                    sell_orders = sorted(sell_orders)[:5] if sell_orders else sell_orders

                #saved_items.update_one(dict(item=item), {'$set':{'buy_orders':buy_orders,'sell_orders':sell_orders,'updated':current_time}},upsert=True)
            
            #Wait between items to keep within 3 API requests per second
            time.sleep(0.35)
            
        item_orders[item] = {'buy_orders':buy_orders,'sell_orders':sell_orders}

    return jsonify({'data':item_orders})




if __name__ == '__main__':
    app.run()