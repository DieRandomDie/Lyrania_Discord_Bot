from os import path
import discord
import asyncio
from discord.ext import commands, tasks
import time
import lyr
import json

client = commands.Bot(command_prefix='!')
channel_id = 934490823100366868

with open('token.dat') as token_data:
    token = token_data.readline()
    print('Token fetched')
    print('Connecting...')
if not path.exists('users.json'):
    print("users.json does not exist. Creating...")
    with open('users.json', 'w') as users_data:
        users_data.write("{\n\t}")
        print("users.json created.")


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.command(name='list')
async def _list(ctx):
    channel = client.get_channel(channel_id)
    await channel.send('Available commands:\n!key [api_key] - saves your data to the bot.\n!update - syncs your data with live api data', delete_after=60)
    print("Successfully ran list command for user, " + str(ctx.author))


@client.command()
async def key(ctx, api_key):
    user_id = str(ctx.author.id)
    # open users in read
    with open('users.json', 'r') as file:
        # converts json to dict
        file_data = json.load(file)
        print(file_data)
        # check if user exists
        if user_id in file_data.keys():
            # update existing user's api key
            file_data[user_id] = api_key
            await ctx.author.send('API key has been updated. You may now return to the server or use commands here.')
        else:
            # add new user
            file_data[user_id] = api_key
            await ctx.author.send('API key has been added. You may now return to the server or use commands here.')
    # open users in write (to truncate file)
    with open('users.json', 'w') as file:
        json.dump(file_data, file, indent=4)
    if ctx.channel.id == channel_id:
        await ctx.message.delete()
    print("Successfully ran key command for user, " + str(ctx.author))


@client.command()
async def update(ctx):
    channel = client.get_channel(channel_id)
    user_id = str(ctx.author.id)
    with open('users.json') as data:
        data_list = json.load(data)
        if user_id in data_list.keys():
            await channel.send('API Key exists...\nUpdating your data...\n'
                               + lyr.api_update(user_id), delete_after=10)
        else:
            await channel.send("API key doesn't exist. Sent a message with instructions.", delete_after=10)
            await ctx.author.send('I need your api key to pull data from Lyrania. Please respond with !lyr key [key]')
            print('Sent API key request to ' + user_id)
    print("Successfully ran update command for user, " + str(ctx.author))


@client.command()
async def exp(ctx, start, end, current_xp):
    channel = client.get_channel(channel_id)
    user_id = str(ctx.author.id)
    await channel.send("This is in development, sorry!")


# @tasks.loop(seconds=timer)
# async def alarm_message():
#     await client.wait_until_ready()
#     channel = client.get_channel(channel_id)
#     message = 'test'
#     await channel.send(message)


# alarm_message.start()

client.run(token)
