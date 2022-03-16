import math

import discord
import asyncio
import json
from datetime import datetime as dt
import pytz
from discord.ext import commands, tasks
from lyr import api_update, fetch, checkfile

client = commands.Bot(command_prefix='!', help_command=None)
# Check for bot.dat file
if not checkfile('bot.dat'):
    # create file
    with open('bot.dat', 'w') as token_data:
        # request token
        token_data.write(input("Bot token: "))
with open('bot.dat') as bot_data:
    token = bot_data.readline().strip()
    print(f'Token fetched.')
    server_id = int(bot_data.readline().strip())
    print(f'Server ID, {server_id}, fetched.')
    channel_id = int(bot_data.readline().strip())
    print(f'Channel ID, {channel_id}, fetched.')
    notify = int(bot_data.readline().strip())
    print(f'Notif Rank ID, {notify}, fetched.')
    print('Connecting...')
if not checkfile('users.json'):
    print("users.json does not exist. Creating...")
    with open('users.json', 'w') as users_data:
        users_data.write("{\n\t\n}")
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


@client.command(name='list')
async def _list(ctx):
    await ctx.reply(
        'Available commands:\n'
        '>>> !key <api_key> - saves your data to the bot. (use in DMs)\n'
        '!update - syncs your data with live api data.\n'
        '!exp <goal> <opt: current_gains> - shows xp needed for goal level. '
        'Optional argument gives approximate kills to level.\n'
        '!equips <weap> <arm> <opt: blacksmith> - returns costs for upgrades.')
    print("Successfully ran list command for user, {}".format(ctx.author))


@client.command()
async def key(ctx, api_key):
    channel = client.get_channel(channel_id)
    user_id = str(ctx.author.id)
    # open users in read
    if user_id in client.userdata.keys():
        # update existing user's api key
        client.userdata[user_id] = api_key
        response = 'API key has been updated.'
    else:
        # add new user
        client.userdata[user_id] = api_key
        response = 'API key has been added.'
    # open users in write (to truncate file)
    with open('users.json', 'w') as file:
        json.dump(client.userdata, file, indent=4)
        print("Saved users.json")
    await ctx.reply(response + ' You may now return to the server or use commands here.')
    print("Successfully ran key command for user, {}".format(ctx.author))
    if ctx.channel == channel:
        await ctx.message.delete()


@client.command()
async def update(ctx):
    user_id = str(ctx.author.id)
    if user_id in client.userdata.keys():
        await ctx.reply('>>> API Key exists...\nUpdating your data...\n' + api_update(client.userdata, user_id))
    else:
        await ctx.reply("API key doesn't exist. Sent a message with instructions.")
        await ctx.author.send('I need your api key to pull data from Lyrania. Please respond with !key <key>')
        print('Sent API key request to ' + user_id)
    print("Successfully ran update command for user, {}".format(ctx.author))


@client.command()
async def exp(ctx, end, current_xp=0):
    user_id = str(ctx.author.id)
    start = int(fetch(user_id, "level")) + 1
    end = int(end)
    current_xp = int(current_xp)
    xp_needed = round(((end - start) / 2) * (start + end) * 25)
    response = 'You need {xp:,} exp to reach level {lv:,}.'.format(xp=xp_needed, lv=end)
    if current_xp > 0:
        response += '\nThis will take approximately {k:,} kills.'.format(k=round(xp_needed / current_xp))
    await ctx.reply(">>> "+response)


@client.command()
async def notifyme(ctx):
    member = ctx.author
    role = discord.utils.get(ctx.guild.roles, name="Notifications")
    await member.add_roles(role)
    await ctx.reply('You have been given the "Notifications" role.')
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
    fixed_equipment = {}
    for keys in equipment.keys():
        equip = keys.split(" ")[1]
        orb = keys.split(" ")[0]
        level = equipment[keys]
        fixed_equipment[equip] = {}
        fixed_equipment[equip]['orb'] = orb
        fixed_equipment[equip]['level'] = level
    weap_cost = 0
    arms_cost = 0
    discount = 1 - bsmith/100
    shortsword = int(fixed_equipment['shortsword']['level'])
    dagger = int(fixed_equipment['dagger']['level'])
    helmet = int(fixed_equipment['helmet']['level'])
    shoulders = int(fixed_equipment['shoulders']['level'])
    wrist = int(fixed_equipment['wrist']['level'])
    gloves = int(fixed_equipment['gloves']['level'])
    chestpiece = int(fixed_equipment['chestpiece']['level'])
    leggings = int(fixed_equipment['leggings']['level'])
    boots = int(fixed_equipment['boots']['level'])

    for i in range(shortsword + 1, int(gweaps) + 1):
        weap_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
    for i in range(dagger + 1, int(gweaps) + 1):
        weap_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
    for i in range(helmet + 1, int(garms) + 1):
        arms_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
    for i in range(shoulders + 1, int(garms) + 1):
        arms_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
    for i in range(wrist + 1, int(garms) + 1):
        arms_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
    for i in range(gloves + 1, int(garms) + 1):
        arms_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
    for i in range(chestpiece + 1, int(garms) + 1):
        arms_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
    for i in range(leggings + 1, int(garms) + 1):
        arms_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
    for i in range(boots + 1, int(garms) + 1):
        arms_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
    await ctx.reply(f'>>> Weapons: ({shortsword}, {dagger}) to {gweaps} costs {math.ceil(weap_cost):,}\n'
                    f'Armours: ({helmet}, {shoulders}, {wrist}, {gloves}, {chestpiece}, {leggings}, {boots}) to {garms} costs {math.ceil(arms_cost):,}')


@tasks.loop(seconds=1)
async def alarm_message():
    await client.wait_until_ready()
    channel = client.get_channel(channel_id)
    general = client.get_channel(697818339992666205)
    time = dt.now(tz=pytz.timezone('Europe/London'))
    hour, minute, second = time.hour, time.minute, time.second
    if minute == 45 and hour % 2 == 0 and second == 0:
        await channel.send('<@&{}> Get area boss contract!'.format(notify), delete_after=600)
        print("Sent contract alert at {}".format(time))
    if minute == 0 and hour % 2 == 1 and second == 0:
        await channel.send('<@&{}> Fight area boss!'.format(notify), delete_after=600)
        print("Sent fight alert at {}".format(time))
    if minute == 0 and hour == 19 and second == 0:
        await general.send('@everyone guild boss in 15 minutes.', delete_after=600)
    if minute == 13 and hour == 19 and second == 0:
        await channel.send('<@&{}> Almost time for guild boss. Get ready!'.format(notify), delete_after=600)
        print("Sent guild boss alert at {}".format(time))

alarm_message.start()
client.run(token)
