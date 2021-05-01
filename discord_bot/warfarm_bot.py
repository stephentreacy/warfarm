"""Warfarm Bot

A Discord bot that can save tenno.zone links for users and get up to date prices from warframe.market"""

import discord
import pymongo
import requests
import os

def help_message():
    """Create Embeded message with available commands"""
    embed_help = discord.Embed(title='Avilable Commands')
    embed_help.add_field(name='$hi', value='Say hello', inline=False)
    embed_help.add_field(name='$view', value='Show database (Not to you though)', inline=False)
    embed_help.add_field(name='$link https://tenno.zone/planner/<unique ID>', value='Save tenno.zone link.', inline=False)
    embed_help.add_field(name='$items', value='Show orders of items from warframe.market.', inline=False)

    return embed_help

client_disc = discord.Client()

@client_disc.event
async def on_ready():
    print(f'Logged in as {client_disc.user}')

@client_disc.event
async def on_message(message):
    """Reads message on Discord and replies to commands"""
    
    #Ignores messages sent by bot
    if message.author == client_disc.user:
        return

    #Test case to check bot is replying
    if message.content == '$hi':
        await message.channel.send('hello')

    #Create Embeded message with commands
    if message.content == '$help':
        await message.channel.send(embed=help_message())

    #View database contents in console, for testing purposes.
    if message.content == '$view':
        await message.channel.send('You have no power here')
        for user in user_links.find():
            print(user)

    #Saves link to MongoDB
    if message.content.startswith('$link '):
        #Delete the message to prevent others using the link
        await message.delete()
        ack_message = await message.channel.send(f'Received link command from {message.author.mention}. Please wait...')

        try:
            link = message.content.split()[1]

            if not link.startswith('https://tenno.zone/planner/') or link == 'https://tenno.zone/planner/':
                raise ValueError

            user_links.update_one(dict(user=message.author.id), {'$set':{'link':link}},upsert=True)

        except ValueError:
            await message.channel.send(f'{message.author.mention} Enter a valid link or type $help.')
        except Exception as err:
            print(err)
            await message.channel.send(f'{message.author.mention} Cannot connect to database. Please try again.')
        else:
            await message.channel.send(f'Successfully added tenno.zone link for {message.author.mention}')
        finally:
            await ack_message.delete()

    #Get link from database and replies with messages containing item orders
    if message.content == '$items':
        #TODO Check user is in DB, check for div with error in HTML that the link is valid
        
        ack_message = await message.channel.send(f'Received items command from {message.author.mention}. Please wait...')

        link=user_links.find_one({'user':message.author.id},{'link':1})['link']

        response = requests.get('http://127.0.0.1:5000/items', params={'link':link})
        data = response.json()['data']

        #Create Embeded message for items
        embed_items = discord.Embed(title="Warframe.Market Orders", colour=discord.Colour(0xdaeb67), description=message.author.mention)

        item_count = 0
        for item in data:
            embed_items.add_field(name="Item", value="[**"+item+"**](https://warframe.market/items/"+ item.lower().replace(' ','_').replace('-','_').replace("'",'').replace('&','and')+")",inline=True)
            embed_items.add_field(name="Buy Orders", value=data[item]['buy_orders'], inline=True)
            embed_items.add_field(name="Sell Orders", value=data[item]['sell_orders'], inline=True)
            item_count += 1

            #Embeded messages can take a max of 8 items. Make a new message for the rest of the items
            if item_count == 8:
                await message.channel.send(embed=embed_items)
                embed_items = discord.Embed(title="Warframe.Market Orders", colour=discord.Colour(0xdaeb67), description=message.author.mention)
                item_count = 0
                
        await message.channel.send(embed=embed_items)
        await ack_message.delete()

if __name__ == '__main__':
    client_db = pymongo.MongoClient()
    warfarm_db = client_db['warfarm_db']
    user_links = warfarm_db['user_links']

    client_disc.run(os.getenv('TOKEN'))