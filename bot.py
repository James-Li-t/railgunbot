import discord
import os
import requests
import json
import random
import math
import praw
import warnings
import oppaipy

from osuapi import OsuApi, ReqConnector, OsuMod
from datetime import timedelta, datetime, date
from discord.ext import commands

reddit = praw.Reddit(client_id='UIpkKGFsuHpFQQ', client_secret='nlIBmAO7V0TPI-DXsoq_-OiYYEc',
                     username='beep_boop_botterino', password='HjJWMvwF', user_agent='disc')

api = OsuApi("8a5b59a0b63e5aaf6be7a263b0006e4030bf6005",
             connector=ReqConnector())
x = '.'
client = commands.Bot(command_prefix=x)
client.remove_command('help')


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game('.help for commands!'))
    print("WE live boys can i get a pogU in the chat")


@client.command()
async def help(ctx):
    await ctx.send(f"""
```diff
+ Here are all the currently availible commands!

+ Current command prefix: '{x}'

+ help → Displays this menu.
+ gifme [query] → Returns a gif with the given search term.
+ ping → Returns the bots current ping.
+ emojify [emoji names] → Turns text into emojis.
+ redhot [subreddit] [amount] → Generates posts from the hot section of a subreddit.

+ osu! Commands ↓

+ rec [osu! username] → Shows information about the most recent play of the given player.
```
""")


@client.command()
async def ping(ctx):
    await ctx.send(f':boom: {round(client.latency * 1000)}ms')


@client.command()
async def emojify(ctx, *, input):
    temp = input.split()
    x = []
    for words in temp:
        x.append(f' :{words}: ')

    await ctx.send("".join(x))


@client.command()
async def gifme(ctx, *, input):
    holder = input
    input.replace(' ', '+')
    loadinfo = {'api_key': 'YhiYyh2k0z9TjQkhqVHE0lT55dBIkFT2',
                'q': f'{input.lower()}', 'limit': '10', 'offset': '0', 'rating': 'r', 'lang': 'en'}
    data = requests.get(
        'https://api.giphy.com/v1/gifs/search', params=loadinfo)
    dat = data.json()
    await ctx.send(f'**Here is the  *{holder}*  gif you have requested** :clap: ' + '\n' + dat['data'][0]['url'])


@client.command()
async def redhot(ctx, subx, amnt):

    generate = int(amnt)

    if generate <= 10:

        sub = reddit.subreddit(subx)
        hot = sub.hot(limit=generate)
        x = 0

        scount = sub.hot(limit=2)
        for i in scount:
            if i.stickied:
                x += 1

        hotx = sub.hot(limit=generate + x)

        postcount = 1
        colors = [0xff0000, 0xff4000, 0xff8000, 0xff9900, 0xffbf00,
                  0xffff00, 0xbfff00, 0x80ff00, 0x40ff00, 0x00ff00, 0x00ff40]
        coloriter = iter(colors)

        try:
            for post in hotx:
                if not post.stickied:

                    title = post.title
                    url = post.shortlink
                    ups = post.ups
                    thumb = post.thumbnail
                    auth = post.author
                    comments = post.num_comments

                    if post.spoiler:
                        thumb = "https://i.redd.it/mjp156w2osv11.jpg"
                    if post.is_self:
                        thumb = "https://www.adweek.com/wp-content/uploads/2019/10/Reddit-Logo-Horizontal.png"

                    time = (datetime.utcfromtimestamp(
                        post.created).strftime('%Y-%m-%d %H:%M:%S'))

                    embed = discord.Embed(
                        title=title, url=url, description=None, color=next(coloriter))
                    embed.set_author(name='#' + str(postcount) +
                                     " Hottest Post on /r/" + str(subx))
                    embed.set_thumbnail(url=str(thumb))
                    embed.add_field(name=str(ups) + " upvotes :thumbsup:",
                                    value=str(comments) + " comments :speech_left:", inline=False)
                    embed.set_footer(text="Posted by /u/" +
                                     str(auth) + " on " + str(time))
                    postcount += 1

                    await ctx.send(embed=embed)
        except:
            await ctx.send("**Subreddit not found!**")

    else:
        await ctx.send("**Please enter a maximum of 10 Hot posts to generate!**")


#Osu Section
@client.command()
async def rec(ctx, username):
    warnings.filterwarnings("ignore")
    try:
        calc = oppaipy.Calculator()
        user = username

        def acc(n50, n100, n300, n0):
            top = (50*n50 + 100*n100 + 300*n300)
            bot = 300 * (n0 + n50 + n100 + n300)
            accuracy = top / bot
            return accuracy

        warnings.filterwarnings("ignore")

        results = api.get_user_recent(username=user, limit=1)
        user_ = api.get_user(username=user)
        mapid = results[0].beatmap_id
        mod = results[0].enabled_mods
        m = ""

        if str(mod) == "NoMod":
            m = "NoMod"
        else:
            m = mod.shortname
        beatmap = api.get_beatmaps(beatmap_id=mapid)
        mapset = str(beatmap[0].beatmapset_id)
        mode = str(beatmap[0].mode)

        miss = results[0].countmiss
        _50 = results[0].count50
        _100 = results[0].count100
        _300 = results[0].count300
        combo = results[0].maxcombo

        rank = results[0].rank
        userid = results[0].user_id
        score = results[0].score
        timeplayed = results[0].date
        name = user_[0].username

        maptitle = beatmap[0].title
        ver = beatmap[0].version
        combomax = beatmap[0].max_combo
        star = beatmap[0].difficultyrating
        mapper = beatmap[0].creator

        accuracy = acc(n50=_50, n100=_100, n300=_300, n0=miss)
        accuracy = round(accuracy*100, 2)

        new_mode = ""
        if mode == "osu!standard":
            new_mode = 'osu'
        elif mode == "osu!taiko":
            new_mode = 'taiko'
        elif mode == "osu!mania":
            new_mode = 'mania'
        elif mode == "osu!catchthebeat":
            new_mode = 'fruits'

        mod_ = 0
        if OsuMod.NoFail in mod:
            mod_ |= 1
        if OsuMod.DoubleTime in mod:
            mod_ |= 64
        if OsuMod.Easy in mod:
            mod_ |= 2
        if OsuMod.HardRock in mod:
            mod_ |= 16
        if OsuMod.Flashlight in mod:
            mod_ |= 1024
        if OsuMod.Hidden in mod:
            mod_ |= 8
        if OsuMod.Nightcore in mod:
            mod_ |= 512
        if OsuMod.HalfTime in mod:
            mod_ |= 256

        url = f"https://osu.ppy.sh/beatmapsets/{mapset}#{new_mode}/{mapid}"
        thumbnail = f"https://b.ppy.sh/thumb/{mapset}l.jpg"
        icon = f"https://a.ppy.sh/{userid}"
        prof = f"https://osu.ppy.sh/users/{userid}"

        dl_url = f"https://osu.ppy.sh/osu/{mapid}"
        r = requests.get(dl_url, allow_redirects=True)
        open('meta.osu', 'wb').write(r.content)

        calc.set_beatmap("meta.osu")
        calc.set_mods(mod_)
        calc.set_combo(combo)
        calc.set_accuracy(_100, _50)
        calc.set_misses(miss)
        calc.calculate()
        pp = round(calc.pp, 2)
        calc.reset()
        calc.set_beatmap("meta.osu")
        calc.set_mods(mod_)
        calc.set_accuracy_percent(accuracy)
        calc.calculate()
        ppfc = round(calc.pp, 2)
        calc.set_beatmap("meta.osu")
        calc.set_mods(mod_)
        calc.calculate()
        ppmax = round(calc.pp, 2)

        file = open('meta.osu', 'r+')
        file.truncate(0)
        file.close()
        calc.close()

        nowtime = datetime.utcnow()
        difference = nowtime - timeplayed
        seconds = round(difference.total_seconds())
        x = timedelta(seconds = seconds)

        if rank == "X":
            embed = discord.Embed(
                title=f"Played by {name}  **{accuracy}%**  [{round(pp,2)}pp]", url=prof, description=f"Mapped by {mapper}", color=0xfe58a3)
            embed.set_author(
                name=f"{maptitle} ({ver} [{round(star, 2)}☆] [{m}]) ", url=url, icon_url=icon)
            embed.set_thumbnail(url=thumbnail)
            embed.add_field(
                name=f":point_right: Rank: **{rank}** :point_right:  **{combo}x / {combomax}x**  :point_right: **{score}** ", value=f"**:arrow_forward: [{_300}/{_100}/{_50}/{miss}]**", inline=True)
            embed.set_footer(
                text=f"Played on {timeplayed} UTC [{x} ago]")
        else:
            embed = discord.Embed(
                title=f"Played by {name}  **{accuracy}%**  [{round(pp,2)}pp]", url=prof, description=f"Mapped by {mapper}", color=0xfe58a3)
            embed.set_author(
                name=f"{maptitle} ({ver} [{round(star, 2)}☆] [{m}]) ", url=url, icon_url=icon)
            embed.set_thumbnail(url=thumbnail)
            embed.add_field(
                name=f":point_right: Rank: **{rank}** :point_right:  **{combo}x / {combomax}x**  :point_right: **{score}** ", value=f"**:arrow_forward: [{_300}/{_100}/{_50}/{miss}]  [{round(ppfc,2)}pp for FC, {round(ppmax,2)}pp for SS]**", inline=True)
            embed.set_footer(
                text=f"Played on {timeplayed} UTC [{x} ago]")

        await ctx.send(embed=embed)

    except ValueError:
        await ctx.send("**Information on this beatmap is currently not available, sorry!**")
    except IndexError:
        await ctx.send(f"**{username} has not recently played any songs**")
    except:
        await ctx.send("**Something broke, try again later or contact @Li James#5602**")

@client.command()
async def rrank(ctx):
    warnings.filterwarnings("ignore")
    lim = 100
    yesterday = date.today() - timedelta(days=1)

    while True:
        try:
            results = api.get_beatmaps(since = yesterday, limit = lim)
            break
        except ValueError:
            lim -= 2
            continue

    maps = []
    for map in results:
        if str(map.approved) == 'BeatmapStatus.ranked':
            maps.append(map.beatmapset_id)

    rrmapid = maps[len(maps) - 1]
    rrmap = api.get_beatmaps(beatmapset_id = rrmapid)

    maptitle = rrmap[0].title
    mapper = rrmap[0].creator
    bpm = rrmap[0].bpm
    stime = rrmap[0].total_length
    time = timedelta(seconds = stime)
    artist = rrmap[0].artist
    rdate = rrmap[0].approved_date

    thumbnail = f"https://b.ppy.sh/thumb/{rrmapid}l.jpg"
    url = f"https://osu.ppy.sh/beatmapsets/{rrmapid}"

    embed=discord.Embed(title="View Mapset", url= url, description=f"Created by {mapper}", color=0xa825e4)
    embed.set_author(name=f"{maptitle} - {artist}")
    embed.set_thumbnail(url=thumbnail)
    embed.add_field(name=f"Bpm: [{bpm}] ",value = f"**Length: [{time}]**", inline=False)
    embed.set_footer(text=f"Ranked on [{rdate}]")

    await ctx.send("**Here is the most recently ranked std map: **")
    await ctx.send(embed=embed)



client.run('NzMwNDgyODI0NDczMzQ2MDkw.Xwy67g.FCWQcyfH_K9TxemwqPaC-XnggmY')
