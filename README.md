# Warfarm
Single Page Application and Discord Bot to retrieve prices from warframe.market. Used to get a quick overview of prices and decide if the item should be bought or farmed in game.

Merges [warfarm_bot](https://github.com/stephentreacy/warfarm_bot) and [warframe_buy_or_farm](https://github.com/stephentreacy/warframe_buy_or_farm)

# Warfarm API

Receives [tenno.zone](https://tenno.zone/planner/) ID and retrieves selected items from [tenno.zone](https://tenno.zone/planner/) and makes requests to the [warframe.market](https://warframe.market/) API to get current buy and sell orders for each item. Item orders are saved to MongoDB and orders from database are used if last request was recent.

To be hosted using AWS Lambda.

# WarfarmBot

Discord bot to interact with Warfarm API.

Users provide their personal [tenno.zone](https://tenno.zone/planner/) link to be saved to a database.

User can use $items command to request orders.

Gets JSON from API and creates embeded messages containing a [warframe.market](https://warframe.market/) link for each item and the most relevant buy and sale orders.

![Example Image](https://raw.githubusercontent.com/stephentreacy/warfarm/main/images/discord_bot_example.png)

# SPA
To be written in Vue.js


