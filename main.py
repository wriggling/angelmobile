import discord
from discord.ext import commands
import colorama
from colorama import Fore
import requests
import websocket
from keep_alive import keep_alive
import os

def clear(): return os.system('cls') if os.name == 'nt' else os.system('clear')

stream_url = "https://www.twitch.tv/9711"

token = os.getenv("token")
prefix = os.getenv("prefix")

clear()


headers = {"Authorization": token, "Content-Type": "application/json"}

validate = requests.get('https://canary.discordapp.com/api/v9/users/@me', headers=headers)
if validate.status_code != 200:
  print(f"{Fore.RED}[ERROR] {Fore.RESET}Your token might be invalid. Please check it again.")
  sys.exit()

userinfo = requests.get('https://canary.discordapp.com/api/v9/users/@me', headers=headers).json()
username = userinfo["username"]
discriminator = userinfo["discriminator"]
userid = userinfo["id"]

intents = discord.Intents.all()
Angel = commands.Bot(command_prefix={prefix}, intents=intents, self_bot=True, help_command=None)

clear()


print(f"""
{Fore.RED}┏┓┳┓┏┓┏┓┓        User: @{username}
{Fore.RED}┣┫┃┃┃┓┣ ┃        ID: {userid}
{Fore.RED}┛┗┛┗┗┛┗┛┗┛       Prefix: {prefix}
          \n\n\n\n                     
""")
@Angel.command()
async def help(ctx):
    await ctx.message.delete()
    await ctx.send(
        f"```ini **[@Angel Stream]** \n Streaming, Listening, Playing, Watching \n Example: \n **[{prefix}s Angel]** | **[{prefix}p Angel]** | **[{prefix}l Angel]** | **[{prefix}w Angel]** \n if you would like to view the aliases type **[{prefix}aliases]**``` ")


@Angel.command()
async def aliases(ctx):
    await ctx.message.delete()
    await ctx.send(
        f"```ini > Streaming = **[{prefix}stream]** | **[{prefix}streaming]** | **{prefix}s** \n > Playing | **[{prefix}playing]** | **[{prefix}play]** | **[{prefix}p]** | **[{prefix}game]**  \n > Listening | **[{prefix}listen]** | **[{prefix}l]** \n > Watching | **[{prefix}watch]** | **[{prefix}w]**```")
      
@Angel.command(aliases=["streamings", "s"])
async def stream(ctx, *, message):
    await ctx.message.delete()
    await ctx.send(content=f"``[ANGEL] Set Streaming to {message}``", delete_after=2),
    stream = discord.Streaming(
        name=message,
        url=stream_url,
    )
    await Angel.change_presence(activity=stream)
    print(f"{Fore.GREEN}[-] Set Streaming Status To: {message}")


@Angel.command(aliases=["play", "p", "game"])
async def playing(ctx, *, message):
    await ctx.message.delete()
    await ctx.send(content=f"``[ANGEL] Set Playing to {message}``", delete_after=2),
    game = discord.Game(
        name=message
    )
    await Angel.change_presence(activity=game)
    print(f"{Fore.GREEN}[-] Set Playing Status To: {message}")


@Angel.command(aliases=["listen", "l"])
async def listening(ctx, *, message):
    await ctx.message.delete()
    await ctx.send(content=f"``[ANGEL] Set Listening to {message}``", delete_after=2),
    await Angel.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=message,
        ))
    print(f"{Fore.GREEN}[-] Set Listening Status To: {message}")


@Angel.command(aliases=["watch", "w"])
async def watching(ctx, *, message):
    await ctx.message.delete()
    await ctx.send(content=f"``[ANGEL] Set Watching to {message}``", delete_after=2),
    await Angel.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=message
        ))
    print(f"{Fore.GREEN}[-] Set Watching Status To: {message}")


@Angel.command(aliases=["sav", "stopstatus", "stoplistening", "stopplaying", "stopwatching", "stopsreaming"])
async def stopactivity(ctx):
    await ctx.message.delete()
    await ctx.send(content=f"``[ANGEL] Stop Activity``", delete_after=1),
    await Angel.change_presence(activity=None, status=discord.Status.dnd)
    print(f"{Fore.RED}Stopped Activity")

@Angel.command()
async def credits(ctx):
    await ctx.message.delete()
    await ctx.send(content=f"**[@AniTool Credits]** \n\n **``Creator: @cxcvc on Discord``** \n **Links: [Github](https://github.com/wriggling)**", delete_after=1)
  
Angel.run(token, bot=false)
keep_alive()
