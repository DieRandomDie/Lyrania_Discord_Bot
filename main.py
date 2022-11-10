import math

import discord
import json
from datetime import datetime
import pytz
from discord.ext import tasks
from lyr import api_update, fetch, checkfile

client = discord.Bot()
# Check for bot.dat file
if not checkfile('bot.dat'):
    # create file
    with open('bot.dat', 'w') as token_data:
        # request token
        data = input("Bot token: ") + "\n"
        data = data + input("Server ID: ") + "\n"
        data = data + input("Notification Channel ID: ") + "\n"
        data = data + input("Notification Rank ID: ") + "\n"
        token_data.write(data)
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


@client.command(description="Set your API key.", hidden=True)
async def key(ctx, api_key: discord.Option(str, description="Your API key is in Settings > Misc.")):
    user_id = str(ctx.author.id)
    if len(api_key) == 32:
        if user_id in client.userdata.keys():  # update existing user's api key
            client.userdata[user_id] = api_key
            response = 'API key has been updated.'
        else:  # add new user
            client.userdata[user_id] = api_key
            response = 'API key has been added.'
        # open users in write (to truncate file)
        with open('users.json', 'w') as file:
            json.dump(client.userdata, file, indent=4)
            print("Saved users.json")
    else:
        response = 'API key should be 32 characters. (I think o.0)'
    await ctx.respond(response, ephemeral=True)


@client.command(description="Update your api data.")
async def update(ctx):
    user_id = str(ctx.author.id)
    if user_id in client.userdata.keys():
        await ctx.respond('>>> API Key exists...\nUpdating your data...\n' + api_update(client.userdata, user_id))
    else:
        await ctx.respond("API key doesn't exist. Please use </key:1039662112760397825>.")
    print(f"Successfully ran update command for user, {ctx.author}")


@client.command(description="Calculate experience needed to level to a given level.")
async def exp(ctx, goal: discord.Option(int, description="The level you want to calculate to."),
              kill_xp: discord.Option(int, description="The amount of exp you get per kill.", required=False)):
    user_id = str(ctx.author.id)
    start = int(fetch(user_id, "level")) + 1
    goal = int(goal)
    kill_xp = int(kill_xp)
    xp_needed = round(((goal - start) / 2) * (start + goal) * 25)
    response = f'You need {xp_needed:,} exp to reach level {goal:,}.'
    if kill_xp > 0:
        k = round(xp_needed / kill_xp)
        response += f'\nThis will take approximately {k:,} kills.'
    await ctx.respond(response)
    print()


@client.command(description="Grants you the Notifications role.")
async def notifyme(ctx):
    member = ctx.author
    role = discord.utils.get(ctx.guild.roles, name="Notifications")
    await member.add_roles(role)
    await ctx.respond('You have been given the "Notifications" role.')
    print(f'{member} has been granted {role} role.')


@client.command(description="Calculate cost for equipment upgrades.")
async def equips(ctx, goal_weaps: discord.Option(int, description="The level you want your weapons to be.", default=0),
                 goal_arms: discord.Option(int, description="The level you want your armors to be.", default=0),
                 blacksmith: discord.Option(int, description="The level of the guild blacksmith", default=50)):
    user_id = str(ctx.author.id)
    try:
        with open(user_id+'.json') as data:
            data = json.load(data)

        equipment = data["equipment"]
        weap_cost = 0
        arms_cost = 0
        discount = 1 - blacksmith / 100
        shortsword = int(equipment['Shortsword']['level'])
        dagger = int(equipment['Dagger']['level'])
        helmet = int(equipment['Helmet']['level'])
        shoulders = int(equipment['Shoulders']['level'])
        wrist = int(equipment['Wrist']['level'])
        gloves = int(equipment['Gloves']['level'])
        chestpiece = int(equipment['Chestpiece']['level'])
        leggings = int(equipment['Leggings']['level'])
        boots = int(equipment['Boots']['level'])

        for i in range(shortsword + 1, int(goal_weaps) + 1):
            weap_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(dagger + 1, int(goal_weaps) + 1):
            weap_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(helmet + 1, int(goal_arms) + 1):
            arms_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(shoulders + 1, int(goal_arms) + 1):
            arms_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(wrist + 1, int(goal_arms) + 1):
            arms_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(gloves + 1, int(goal_arms) + 1):
            arms_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(chestpiece + 1, int(goal_arms) + 1):
            arms_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(leggings + 1, int(goal_arms) + 1):
            arms_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(boots + 1, int(goal_arms) + 1):
            arms_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        if weap_cost or arms_cost:
            response = ">>> "
        else:
            response = "You didn't give a level higher than your current equipment."
        if weap_cost:
            response += f'Weapons: ({shortsword}, {dagger}) to {goal_weaps} costs {math.ceil(weap_cost):,}p'
            if arms_cost:
                response += "\n"
        if arms_cost:
            response += f'Armours: ({helmet}, {shoulders}, {wrist}, {gloves}, {chestpiece}, {leggings}, {boots}) to {goal_arms} costs {math.ceil(arms_cost):,}p'
        await ctx.respond(response)
    except:
        await ctx.respond("Your data does not exist. Please use </update:1039662112760397826>")


@tasks.loop(seconds=1)
async def alarm_message():
    await client.wait_until_ready()
    channel = client.get_channel(channel_id)
    general = client.get_channel(697818339992666205)
    utc = pytz.utc
    lyr = pytz.timezone('Europe/London')
    utc_dt = datetime.now(utc)
    time = utc_dt.astimezone(lyr)
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
