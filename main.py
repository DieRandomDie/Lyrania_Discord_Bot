import math

import discord
import json
from datetime import datetime
import pytz
from discord.ext import tasks
from lyr import api_update, fetch, checkfile, plat

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


async def update(ctx):
    user_id = str(ctx.author.id)
    if user_id in client.userdata.keys():
        print(api_update(client.userdata, user_id))
    else:
        return 0
    print(f"Successfully ran update command for user, {ctx.author}")


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
        await update(ctx)
    else:
        response = 'API key should be 32 characters. (I think o.0)'
    await ctx.respond(response, ephemeral=True)


@client.command(description="Calculate experience needed to level to a given level.")
async def exp(ctx, goal: discord.Option(int, description="The level you want to calculate to."),
              kill_xp: discord.Option(int, description="The amount of exp you get per kill.", default=0, required=False)):
    await update(ctx)
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
                 blacksmith: discord.Option(int, description="The level of the guild blacksmith.", default=50)):
    await update(ctx)
    user_id = str(ctx.author.id)
    embed_var = discord.Embed(title="Equips")

    try:
        with open(user_id+'.json') as userdata:
            userdata = json.load(userdata)

        equipment = userdata["equipment"]
        platinum = plat(userdata["currency"]["money"])
        discount = 1 - blacksmith / 100
        shortsword = int(equipment['Shortsword']['level'])
        shortsword_cost = 0
        dagger = int(equipment['Dagger']['level'])
        dagger_cost = 0
        helmet = int(equipment['Helmet']['level'])
        helmet_cost = 0
        shoulders = int(equipment['Shoulders']['level'])
        shoulders_cost = 0
        wrist = int(equipment['Wrist']['level'])
        wrist_cost = 0
        gloves = int(equipment['Gloves']['level'])
        gloves_cost = 0
        chestpiece = int(equipment['Chestpiece']['level'])
        chestpiece_cost = 0
        leggings = int(equipment['Leggings']['level'])
        leggings_cost = 0
        boots = int(equipment['Boots']['level'])
        boots_cost = 0

        for i in range(shortsword + 1, goal_weaps + 1):
            shortsword_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(dagger + 1, goal_weaps + 1):
            dagger_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(helmet + 1, goal_arms + 1):
            helmet_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(shoulders + 1, goal_arms + 1):
            shoulders_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(wrist + 1, goal_arms + 1):
            wrist_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(gloves + 1, goal_arms + 1):
            gloves_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(chestpiece + 1, goal_arms + 1):
            chestpiece_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(leggings + 1, goal_arms + 1):
            leggings_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount
        for i in range(boots + 1, goal_arms + 1):
            boots_cost += ((0.005 * (i ** 2)) - .0101 * i + .0052) * discount

        weap_cost = shortsword_cost+dagger_cost
        arms_cost = helmet_cost+shoulders_cost+wrist_cost+gloves_cost+chestpiece_cost+leggings_cost+boots_cost

        if weap_cost or arms_cost:
            total_text = ""
            if weap_cost:
                embed_var.add_field(name="Weapons", value="Shortsword:\nDagger:")
                embed_var.add_field(name="Upgrade", value=f"{shortsword} -> {goal_weaps}\n{dagger} -> {goal_weaps}")
                embed_var.add_field(name="Cost", value=f"{math.ceil(shortsword_cost):,}p\n{math.ceil(dagger_cost):,}p")
                # embed_var.add_field(name="\u200b", value="\u200b", inline=False)
                total_text += f"Weapons Cost: {math.ceil(weap_cost):,}p\n"
            if arms_cost:
                embed_var.add_field(name="Armors", value="Helmet:\nShoulders:\nWrist:\nGloves:\nChestpiece:\nLeggings:\nBoots:")
                embed_var.add_field(name="Upgrade", value=f"{helmet} -> {goal_arms}\n{shoulders} -> {goal_arms}\n{wrist} -> {goal_arms}\n{gloves} -> {goal_arms}\n{chestpiece} -> {goal_arms}\n{leggings} -> {goal_arms}\n{boots} -> {goal_arms}")
                embed_var.add_field(name="Cost", value=f"{math.ceil(helmet_cost):,}p\n{math.ceil(shoulders_cost):,}p\n{math.ceil(wrist_cost):,}p\n{math.ceil(gloves_cost):,}p\n{math.ceil(chestpiece_cost):,}p\n{math.ceil(leggings_cost):,}p\n{math.ceil(boots_cost):,}p")
                # embed_var.add_field(name="\u200b", value="\u200b", inline=False)
                total_text += f"Armours Cost: {math.ceil(arms_cost):,}p\n"

            embed_var.add_field(name="Totals", value=f"{total_text}Total Cost:   {math.ceil(weap_cost+arms_cost):,}p", inline=False)
            await ctx.respond(embed=embed_var)

            if platinum - (weap_cost+arms_cost) >= 0:
                await ctx.respond("You can afford this upgrade.", ephemeral=True)
            else:
                need = math.ceil((weap_cost + arms_cost) - platinum)
                await ctx.respond(f"You still need {need:,}p.", ephemeral=True)
        else:
            embed_var.add_field(name="Error", value="You didn't give a level higher than your current equipment.")
            await ctx.respond(embed=embed_var)

    except:
        embed_var.add_field(name="Error", value="Your data does not exist. Please use </key:1040325043516878908>")
        await ctx.respond(embed=embed_var)


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
