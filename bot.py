from os import path
import discord
import asyncio
from discord.ext import commands, tasks
import time
import lyr
import json

client = commands.Bot(command_prefix='!')
channel_id = 934490823100366868
if not path.exists('token.dat'):
    with open('token.dat', 'w') as token_data:
        token_data.write(input("Bot token: "))
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
    channel = client.get_channel(channel_id)
    print(channel)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await channel.send("Hello world!")


@client.command(name='list')
async def _list(ctx):
    await ctx.reply('Available commands:\n!key [api_key] - saves your data to the bot.\n!update - syncs your data with live api data')
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
    print("Successfully ran key command for user, " + str(ctx.author))


@client.command()
async def update(ctx):
    channel = client.get_channel(channel_id)
    user_id = str(ctx.author.id)
    with open('users.json') as data:
        data_list = json.load(data)
        if user_id in data_list.keys():
            await channel.send('API Key exists...\nUpdating your data...\n'
                               + lyr.api_update(user_id))
        else:
            await channel.send("API key doesn't exist. Sent a message with instructions.")
            await ctx.author.send('I need your api key to pull data from Lyrania. Please respond with !lyr key [key]')
            print('Sent API key request to ' + user_id)
    print("Successfully ran update command for user, " + str(ctx.author))


@client.command()
async def exp(ctx, end, current_xp=0):
    channel = client.get_channel(channel_id)
    user_id = str(ctx.author.id)
    start = int(lyr.fetch(user_id, "level"))+1
    end = int(end)
    current_xp = int(current_xp)
    xp_needed = round(((end-start)/2)*(start+end)*25)
    await channel.send('You need {xp:,} exp to reach level {lv:,}.'.format(xp=xp_needed, lv=end))
    if current_xp > 0:
        await channel.send('This will take approximately {k:,} kills.'.format(k=round(xp_needed/current_xp)))


@client.command(name='fetch')
async def get_api(ctx, *args):
    channel = client.get_channel(channel_id)
    user_id = str(ctx.author.id)
    test = lyr.fetch(user_id, args[0])
    await channel.send('Your {x} is {y:,}'.format(x=args[0], y=int(test)))

# @tasks.loop(seconds=timer)
# async def alarm_message():
#     await client.wait_until_ready()
#     channel = client.get_channel(channel_id)
#     message = 'test'
#     await channel.send(message)


# alarm_message.start()

client.run(token)
