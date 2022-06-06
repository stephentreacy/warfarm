This repo is being split into serpeate repos for each part. This page still acts as a summary of the entire project but may be out of date.

- Warfarm API -> [warfarm_api](https://github.com/stephentreacy/warfarm_api)
- WarfarmBot -> Here (will be changed).
- Warfarm SPA -> Not currently in development.

# Warfarm
Single Page Application and Discord Bot to retrieve prices from warframe.market. Used to get a quick overview of prices and decide if the item should be bought or farmed in game.

Merges [warfarm_bot](https://github.com/stephentreacy/warfarm_bot) and [warframe_buy_or_farm](https://github.com/stephentreacy/warframe_buy_or_farm)

# Warfarm API

NOTE: No longer hosted with AWS Lambda or otherwise or uses a DB.

Hosted using AWS Lambda.

Receives [tenno.zone](https://tenno.zone/planner/) ID and retrieves selected items from [tenno.zone](https://tenno.zone/planner/) and makes requests to the [warframe.market](https://warframe.market/) API to get current buy and sell orders for each item. Item orders were saved to MongoDB and orders from database were used if last request was recent. Will update to DynamoDB.

Example request can be seen [here](https://nl8x5g3ujh.execute-api.eu-west-1.amazonaws.com/dev/items?link=rk2ac_B5d)

# WarfarmBot

Discord bot to interact with Warfarm API.

Users provide their personal [tenno.zone](https://tenno.zone/planner/) link to be saved to a database.

User can use $items command to request orders.

Gets JSON from API and creates embeded messages containing a [warframe.market](https://warframe.market/) link for each item and the most relevant buy and sale orders.

![Example Image](https://raw.githubusercontent.com/stephentreacy/warfarm/main/images/discord_bot_example.png)

# SPA
To be written in Vue.js


