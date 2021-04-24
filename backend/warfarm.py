"""Warframe Buy or Farm

Takes a Tenno Zone link from a file
Gets the items selected via checkboxes on website
Shows the price of the items from warframe.market"""

import urllib.request
import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import pandas as pd

def get_mod_dataframe():
    """Returns a dataframe containing all tradable mods"""
    
    #URL of JSON file on github that gets regularly updated
    url = 'https://raw.githubusercontent.com/WFCD/warframe-items/development/data/json/Mods.json'
    
    try:
        json_raw = urllib.request.urlopen(url)
        data = json.loads(json_raw.read())
    except:
        print('Error getting mod list')
        df_mods = pd.DataFrame()
    else:
        df_mods = pd.DataFrame(data)
        df_mods = df_mods[df_mods['tradable']]
        df_mods.drop_duplicates(subset=['name'], inplace=True, ignore_index=True)
    finally:
        return df_mods[['name','rarity']]

def create_mod_stats_file():

    df_mod_stats = pd.DataFrame()

    df_mods = get_mod_dataframe()

    for mod in df_mods.values:

        stats = get_market_prices(mod[0])
        
        if stats:
            df_stats = pd.json_normalize(stats['statistics_closed']['90days'])
            try:
                df_stats['datetime']= pd.to_datetime(df_stats['datetime'])
                latest_series = df_stats.iloc[df_stats['datetime'].idxmax()]
                latest_series['name'] = mod[0]
                latest_series['rarity'] = mod[1]
                latest_series['datetime'] = latest_series['datetime'].date()
                df_mod_stats  = df_mod_stats.append(latest_series)
            except:
                print("There's something wrong with" + mod[0])

        time.sleep(0.4)

    df_mod_stats.to_csv('mod_stats.csv', index=False)

def get_mods_stats_file():
    df_mod_stats = pd.read_csv("mod_stats.csv")
    df_mod_stats['url'] = df_mod_stats['name'].str.lower().str.replace(' ','_').str.replace('-','_').str.replace("'",'').str.replace('&','and')
    df_mod_stats['url'] = "<a href='https://warframe.market/items/" + df_mod_stats['url'] + "'>" + df_mod_stats['name'] + '</a>'
    html = df_mod_stats.to_html(escape=False)
    return html

def get_item_list(url):
    """Returns the list of items from tenno.zone link.

    PARAMETERS:
        url -  URL of the tenno.zone link"""

    item_names = []

    #Open the URL as a headless Firefox instance
    print(f'Attempting to open {url} ...')
    opts = Options()
    opts.headless = True
    
    try:
        browser = webdriver.Firefox(options=opts)
        browser.get(url)
    except:
        print(f'Error connecting to {url}')
    else:
        print('Connected to tenno zone, retrieving items...')
        expand_checkbox = browser.find_element_by_xpath("//*[contains(text(), 'Include vaulted sets')]")
        browser.execute_script("arguments[0].click();", expand_checkbox.find_element_by_tag_name('input'))
        items = browser.find_elements_by_class_name('part-set')
        
        for item in items:
            parts = item.find_elements_by_tag_name('label')
            for part in parts:
                if part is parts[0]: item_name = part.text.title()

                if part.find_element_by_tag_name('input').is_selected():
                    if item_name != part.text.title():
                        if part.text.title().find('Neuroptics') > -1: item_names.append(item_name + ' Neuroptics')
                        elif part.text.title().find('Systems') > -1: item_names.append(item_name + ' Systems')
                        elif part.text.title().find('Chassis') > -1: item_names.append(item_name + ' Chassis')
                        else: item_names.append(item_name + ' ' + part.text.title())              
                    else: item_names.append(item_name + ' Set')
    finally:
        browser.quit()
        
    return item_names

def get_market_prices(item, type='mod'):
    """Create a dictionary for statistics or orders for the item"""

    api_url = 'https://api.warframe.market/v1/items/'
    name_url = item.lower().replace(' ','_').replace('-','_').replace("'",'').replace('&','and')
    catagory = 'statistics' if type == 'mod' else 'orders'
    url_item = api_url + name_url + '/' + catagory

    try:
        json_url_item = urllib.request.urlopen(url_item)
    except:
        print(f'Item: {item} not found')
    else:
        item_json = json.loads(json_url_item.read())
        return item_json['payload']



if __name__ == '__main__':

    item_orders = {}

    items = get_item_list('https://tenno.zone/planner/Sk1Snn14E')
    print('Items Retrieved', items)

    for item in items:
        orders = get_market_prices(item, 'item')
        if orders:
            df_orders = pd.json_normalize(orders['orders'])
            df_sell = df_orders[(df_orders['user.status'] == 'ingame') & (df_orders['order_type'] == 'sell')]
            df_buy = df_orders[(df_orders['user.status'] == 'ingame') & (df_orders['order_type'] == 'buy')]
            sell_orders = df_sell.nsmallest(5, 'platinum')['platinum'].values
            buy_orders = df_buy.nlargest(5, 'platinum')['platinum'].values
            item_orders.update({item : [sell_orders, buy_orders, item.lower().replace(' ','_').replace('-','_').replace("'",'').replace('&','and')]})
        time.sleep(0.4)
    print(item_orders)

            
            



