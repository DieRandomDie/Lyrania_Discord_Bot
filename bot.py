import discord
import asyncio
import json
from datetime import datetime as dt
import pytz
from discord.ext import commands, tasks
from lyr import api_update, fetch, checkfile

client = commands.Bot(command_prefix='!')
server_id = 799086296433164328
channel_id = 934490823100366868
notify = 936613130300182528
# Check for token.dat file
if not checkfile('token.dat'):
    # create file
    with open('token.dat', 'w') as token_data:
        # request token
        token_data.write(input("Bot token: "))
with open('token.dat') as token_data:
    token = token_data.readline()
    print('Token fetched')
    print('Connecting...')
if not checkfile('users.json'):
    print("users.json does not exist. Creating...")
    with open('users.json', 'w') as users_data:
        users_data.write("{\n\t}")
        print("users.json created.")
# create dict for user_data
with open('users.json') as user_data:
    client.userdata = json.load(user_data)


@client.event
async def on_ready():
    channel = client.get_channel(channel_id)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await channel.send("I have risen.", delete_after=10)


@client.command(name='list')
async def _list(ctx):
    await ctx.reply(
        'Available commands:\n'
        '!key [api_key] - saves your data to the bot.\n'
        '!update - syncs your data with live api data.\n'
        '!exp <goal> <opt: current_gains> - shows xp needed for goal level.\n'
        '!equips <weap> <arm> <opt: blacksmith> - returns costs for upgrades.', delete_after=120)
    print("Successfully ran list command for user, {}".format(ctx.author))


@client.command()
async def key(ctx, api_key):
    channel = client.get_channel(channel_id)
    user_id = str(ctx.author.id)
    # open users in read
    if user_id in client.userdata.keys():
        # update existing user's api key
        client.userdata[user_id] = api_key
        await ctx.reply('API key has been updated. You may now return to the server or use commands here.',
                        delete_after=30)
    else:
        # add new user
        client.userdata[user_id] = api_key
        await ctx.reply('API key has been added. You may now return to the server or use commands here.',
                        delete_after=30)
    # open users in write (to truncate file)
    with open('users.json', 'w') as file:
        json.dump(client.userdata, file, indent=4)
        print("Saved users.json")
    print("Successfully ran key command for user, {}".format(ctx.author))
    if ctx.channel == channel:
        await ctx.message.delete()


@client.command()
async def update(ctx):
    user_id = str(ctx.author.id)
    if user_id in client.userdata.keys():
        await ctx.reply('API Key exists...\nUpdating your data...\n' + api_update(client.userdata, user_id))
    else:
        await ctx.reply("API key doesn't exist. Sent a message with instructions.")
        await ctx.author.send('I need your api key to pull data from Lyrania. Please respond with !lyr key [key]')
        print('Sent API key request to ' + user_id)
    print("Successfully ran update command for user, {}".format(ctx.author))


@client.command()
async def exp(ctx, end, current_xp=0):
    user_id = str(ctx.author.id)
    start = int(fetch(user_id, "level")) + 1
    end = int(end)
    current_xp = int(current_xp)
    xp_needed = round(((end - start) / 2) * (start + end) * 25)
    await ctx.reply('You need {xp:,} exp to reach level {lv:,}.'.format(xp=xp_needed, lv=end))
    if current_xp > 0:
        await ctx.reply('This will take approximately {k:,} kills.'.format(k=round(xp_needed / current_xp)),
                        delete_after=30)


@client.command()
async def notifyme(ctx):
    member = ctx.author
    role = discord.utils.get(ctx.guild.roles, name="Notifications")
    await member.add_roles(role)
    await ctx.reply('You have been given the "Notifications" role.', delete_after=30)
    print('{} has been granted {} role.'.format(member, role))


@client.command(name='fetch')
async def get_api(ctx, *args):
    user_id = str(ctx.author.id)
    test = fetch(user_id, args[0])
    await ctx.reply('Your {x} is {y:,}'.format(x=args[0], y=int(test)))


@client.command()
async def equips(ctx, gweaps=0, garms=0, bsmith=50):
    channel = client.get_channel(channel_id)
    user_id = str(ctx.author.id)
    with open(user_id+'.json') as data:
        data = json.load(data)
    equipment = data["equipment"]
    keys = list(data["equipment"])
    weap_cost = 0
    arms_cost = 0
    discount = 1 - bsmith/100
    shortsword, dagger, helmet, shoulders, wrist, gloves, chestpiece, leggings, boots = equipment[keys[6]],\
        equipment[keys[2]], equipment[keys[4]], equipment[keys[7]], equipment[keys[8]], equipment[keys[3]],\
        equipment[keys[1]], equipment[keys[5]], equipment[keys[0]]
    for i in range(int(shortsword) + 1, int(gweaps) + 1):
        weap_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
    for i in range(int(helmet) + 1, int(garms) + 1):
        arms_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
    await ctx.reply('Weapons: {} to {} costs {:,.6f}'.format(shortsword, gweaps, weap_cost*2))
    await ctx.reply('Armours: {} to {} costs {:,.6f}'.format(helmet, garms, arms_cost*7))


@tasks.loop(seconds=1)
async def alarm_message():
    await client.wait_until_ready()
    channel = client.get_channel(channel_id)
    time = dt.now(tz=pytz.timezone('Europe/London'))
    hour, minute, second = time.hour, time.minute, time.second
    if minute == 45 and hour % 2 == 0 and second == 0:
        await channel.send('<@&{}> Get area boss contract!'.format(notify), delete_after=60)
        print("Sent contract alert at {}".format(time))
    if minute == 0 and hour % 2 == 1 and second == 0:
        await channel.send('<@&{}> Fight area boss!'.format(notify), delete_after=60)
        print("Sent fight alert at {}".format(time))
    if minute == 13 and hour == 19 and second == 0:
        await channel.send('<@&{}> Almost time for guild boss. Get ready!'.format(notify), delete_after=60)
        print("Sent guild boss alert at {}".format(time))

alarm_message.start()
client.run(token)
