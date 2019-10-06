import json
import math
from enum import Enum
import discord
import requests
from discord.ext import commands

def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(round(stepper * number, digits * 3)) / stepper

class Mods(Enum):
    NoMod           = 0 # 0
    NF              = 1 # 1
    EZ              = 2 # 10
    Touchscreen     = 4 # 100
    HD              = 8 # 1000
    HR              = 16 # 1 0000
    SD              = 32 # 10 0000
    DT              = 64 # 100 0000
    HT              = 256 # 1 0000 0000
    #NC              = 512   # Only set along with DT. i.e: NC only gives 576
    NC              = 576 # 10 0100 0000
    FL              = 1024 # 100 0000 0000
    SO              = 4096 # 1 0000 0000 0000
    #PF              = 16384 # Only set along with SD. i.e: PF only gives 16416
    PF              = 16416 # 100 0000 0010 0000

discord_api_key = open("./api_keys/discord_api_key.txt", "r")
osu_api_key_open = open("./api_keys/osu_api_key.txt", "r")
osu_api_key = osu_api_key_open.read()
bot = commands.Bot(command_prefix = "$")

@bot.event
async def on_ready():
    print('Logged on as {0.user}!'.format(bot))
    await bot.change_presence(activity=discord.Streaming(name="222 bpm", url="https://twitch.tv/wuzado"))

@bot.event
async def on_message(message):
    print('Message from {0.author} in #{0.channel}: {0.content}'.format(message))
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send(bot.latency)

@bot.command()
async def echo(ctx, *, content:str):
    await ctx.send(content)

@bot.command()
async def hello(ctx):
    await ctx.send('Hello ' + str(ctx.author) + '!')

@bot.command()
async def user_raw(ctx, *, content:str):
    if content == None:
        await ctx.send('No username/ID given')
    else:
        print(osu_api_key)
        request = requests.get('https://osu.ppy.sh/api/get_user', {'k': osu_api_key, 'u': content})
        await ctx.send(request.json())

@bot.command()
async def user(ctx, *, content:str):
    if content == None:
        await ctx.send('No username/ID given')
    else:
        request = requests.get('https://osu.ppy.sh/api/get_user', {'k': osu_api_key, 'u': content})
        request_list = request.json()
        request_json = request_list[0]
        embed = discord.Embed(title = "Data for user " + request_json['username'], description = "Level: " + str(int(truncate(float(request_json['level']), 0))), color=0xeee657)
        embed.add_field(name = "Joined on: ", value = request_json['join_date'])
        embed.add_field(name = "Global rank: ", value = request_json['pp_rank'])
        embed.add_field(name = request_json['country'] + " Country rank: ", value = request_json['pp_country_rank'])
        embed.add_field(name = "PP:", value = str(round(float(request_json['pp_raw']), 2)))
        embed.add_field(name = "Accuracy:", value = str(round(float(request_json['accuracy']), 2)))
        embed.add_field(name = "Playcount:", value = request_json['playcount'])
        await ctx.send(embed=embed)

@bot.command()
async def rs_raw(ctx, *, content:str):
    if content == None:
        await ctx.send('No username/ID given')
    else:
        request = requests.get('https://osu.ppy.sh/api/get_user_recent', {'k': osu_api_key, 'u': content, 'limit': 1})
        request_list = request.json()
        request_json_recent = request_list[0]
        print(request_json_recent)
        await ctx.send(request_json_recent)

        request = requests.get('https://osu.ppy.sh/api/get_beatmaps', {'k': osu_api_key, 'b': request_json_recent['beatmap_id'], 'limit': 1})
        request_list = request.json()
        request_json_beatmap = request_list[0]
        print(request_json_beatmap)
        await ctx.send(request_json_beatmap)

@bot.command()
async def rs(ctx, *, content:str):
    if content == None:
        await ctx.send('No username/ID given')
    else:
        request = requests.get('https://osu.ppy.sh/api/get_user_recent', {'k': osu_api_key, 'u': content, 'limit': 1})
        request_list = request.json()
        request_json_recent = request_list[0]

        request = requests.get('https://osu.ppy.sh/api/get_beatmaps', {'k': osu_api_key, 'b': request_json_recent['beatmap_id'], 'limit': 1})
        request_list = request.json()
        request_json_beatmap = request_list[0]

        accuracy = (int(request_json_recent['count300']) * 300 + int(request_json_recent['count100']) * 100 + int(request_json_recent['count50']) * 50) / ((int(request_json_recent['count300']) * 300 + int(request_json_recent['count100']) * 300 + int(request_json_recent['count50']) * 300 + int(request_json_recent['countmiss']) * 300))

        await ctx.send('**Most Recent osu! Standard Play for ' + content + ':**')
        embed = discord.Embed(title = request_json_beatmap['title'] + ' [' + request_json_beatmap['version'] + '] +' + '[' + str(round(float(request_json_beatmap['difficultyrating']), 2)) + '*]', color=0xeee657)
        embed.add_field(name = "Rank: ", value = request_json_recent['rank'])
        embed.add_field(name = "Score: ", value = request_json_recent['score'])
        #embed.add_field(name = "Mods", value = request_json_recent['enabled_mods'])
        #embed.add_field(name = "PP:", value = str(round(float(request_json['pp_raw']), 2)))
        embed.add_field(name = "Accuracy:", value = str(round(float(accuracy), 2) * 0.01))
        embed.add_field(name = "Combo:", value = request_json_recent['maxcombo'] + '/' + request_json_beatmap['max_combo'])     
        await ctx.send(embed=embed)

bot.run(discord_api_key.read())