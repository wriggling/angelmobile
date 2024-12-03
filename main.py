import os
import sys
import json
import time
import requests
import websocket
from keep_alive import keep_alive

status = "dnd" #online/dnd/idle

GUILD_ID = os.getenv("GUILD_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SELF_MUTE = os.getenv("SELF_MUTE")
SELF_DEAF = os.getenv("SELF_DEAF")

usertoken = os.getenv("TOKEN")
if not usertoken:
  print("[ERROR] Please add a token inside Secrets.")
  sys.exit()

headers = {"Authorization": usertoken, "Content-Type": "application/json"}

validate = requests.get('https://canary.discordapp.com/api/v9/users/@me', headers=headers)
if validate.status_code != 200:
  print("[ERROR] Your token might be invalid. Please check it again.")
  sys.exit()

userinfo = requests.get('https://canary.discordapp.com/api/v9/users/@me', headers=headers).json()
username = userinfo["username"]
discriminator = userinfo["discriminator"]
userid = userinfo["id"]

def joiner(token, status):
    ws = websocket.WebSocket()
    ws.connect('wss://gateway.discord.gg/?v=9&encoding=json')
    start = json.loads(ws.recv())
    heartbeat = start['d']['heartbeat_interval']
    auth = {"op": 2,"d": {"token": token,"properties": {"$os": "Windows 10","$browser": "Google Chrome","$device": "Windows"},"presence": {"status": status,"afk": False}},"s": None,"t": None}
    vc = {"op": 4,"d": {"guild_id": GUILD_ID,"channel_id": CHANNEL_ID,"self_mute": SELF_MUTE,"self_deaf": SELF_DEAF}}
    ws.send(json.dumps(auth))
    ws.send(json.dumps(vc))
    time.sleep(heartbeat / 1000)
    ws.send(json.dumps({"op": 1,"d": None}))

def run_joiner():
  os.system("clear")
  print(f"Logged in as {username}#{discriminator} ({userid}).")
  while True:
    joiner(usertoken, status)
    time.sleep(30)

print(f'''                   
{Fore.RED} _____             _ 
{Fore.BLUE}|  _  |___ ___ ___| |
{Fore.RED}|     |   | . | -_| |
{Fore.BLUE}|__|__|_|_|_  |___|_|
{Fore.RED}          |___|      
{Fore.RESET}-----------{Fore.MAGENTA}------------
{Fore.RESET}USER INFO:
User: {Fore.MAGENTA}@{Fore.RESET}{username}
ID: {Fore.MAGENTA}{userid}{Fore.RESET}
Srvr: {Fore.MAGENTA}{GUILD_ID}
VC: {Fore.MAGENTA}{CHANNEL_ID}
Mute: {Fore.MAGENTA}{SELF_MUTE}{Fore.RESET}
Deaf: {Fore.MAGENTA}{SELF_DEAF}{Fore.RESET}
''')

keep_alive()
run_joiner()
