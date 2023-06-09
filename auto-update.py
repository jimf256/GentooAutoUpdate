#!env/bin/python
import time
import datetime
import shutil
import os.path
import subprocess
import sys
import discord
import logging

# cache script directory, install directory defaults to script directory
script_dir = os.path.abspath(os.path.dirname(__file__))
install_dir = script_dir

# if there is a commandline parameter, we use this as the install directory and also
# disable logging to stdout (we're likely running from boot in this case)
quiet = False
if len(sys.argv) > 1:
    install_dir = sys.argv[1].strip()
    quiet = True

# cache today's date timestamp and logfile path
timestamp = datetime.date.strftime(datetime.date.today(), "%d-%m-%Y")
log_file = os.path.join(script_dir, f'log.txt')

def Log(text, stdout=True, logout=True):
    if not quiet and stdout:
        print(f'   auto-update: {text}')
    if logout:
        with open(log_file, 'a') as f:
            f.write(text.strip() + '\n')

def DeleteLog():
    if os.path.isfile(log_file):
        os.remove(log_file)

def Shutdown():
    subprocess.Popen('(sleep 60 && poweroff) &', shell=True)
    Log('auto-update finished!')
    Log('poweroff in 60 seconds...')

def RunProc(cmd, stdout=True, logout=True):
    Log(f'running cmd: "{cmd}"', stdout)
    proc = subprocess.run(cmd, capture_output=True, shell=True, text=True)
    output = proc.stdout.strip()
    Log('------------ output start ------------', stdout, logout)
    Log(output, stdout, logout)
    Log('------------ output end --------------', stdout, logout)
    return output

DeleteLog()
Log(f'', stdout=False)
Log(f'started update for {timestamp}', stdout=False)
Log(f'script directory: {script_dir}', stdout=False)
Log(f'install directory: {install_dir}', stdout=False)

# load discord secrets from config file
discord_bot_token=''
discord_channel_id=''
with open('/etc/auto-update.conf', 'r') as f:
    for line in [x.strip() for x in f.readlines()]:
        if line.startswith('#'):
          continue
        if line.startswith('channel_id: '):
            discord_channel_id = int(line[len('channel_id: '):])
        elif line.startswith('bot_token: '):
            discord_bot_token = line[len('bot_token: '):]
if discord_bot_token == '' or discord_channel_id == '':
    Log(f'failed to load discord channel id/bot token from /etc/auto-update.conf')
    sys.exit(0)
else:
    Log(f'successfully loaded config')

# query kernel boot params
params = RunProc('cat /proc/cmdline', stdout=False)

# check for parameter
param = '-auto_update'
if params and param not in params:
    Log(f'boot param: {param} not found')
    sys.exit(0)
Log(f'boot param: {param} was detected!')

# globally enable stdout logging from this point
quiet = False

# check for last_update.txt, and if found check its contents and
# compare the date to see if an update has already taken place today or not
needs_update = True
timestamp_file = os.path.join(install_dir, 'last_update.txt')
Log('checking if automatic update is necessary...')
if os.path.isfile(timestamp_file):
    with open(timestamp_file, 'r') as f:
        line = f.readline().strip()
        if line and line == timestamp:
            Log('timestamp file found, up to date')
            needs_update = False
        else:
            Log('timestamp file found, out of date')
else:
    Log('timestamp file not found')

Log(f'update required: {needs_update}')
if needs_update == False:
    Shutdown()
    sys.exit(0)

# delete and recreate the timestamp file
if os.path.isfile(timestamp_file):
    os.remove(timestamp_file)
with open(timestamp_file, 'w') as f:
    f.write(timestamp)
Log('new timestamp file written')

# run emaint sync
RunProc('emaint sync --auto', logout=False)
# run emerge command with --pretend to get package output
packages = RunProc('emerge --pretend --verbose --update --deep --changed-use @world')
if 'Total: 0 packages, Size of downloads: 0 KiB' in packages:
    Log('no packages needed updating')
else:
    # run emerge with --quiet
    RunProc('emerge --quiet --update --deep --changed-use @world')
    # run emerge --depclean with --pretend (still must be done manually)
    RunProc('emerge --pretend --depclean')
    # run eclean-dist
    RunProc('eclean-dist --deep')
    # run eclean-pkg
    RunProc('eclean-pkg --deep')

# create the discord client
intents = discord.Intents.default()
log_handler = None

# handle both version 1.7.3 and 2+
if discord.version_info.major > 1:
    intents.message_content = True
    log_handler = discord.utils.setup_logging()
else:
    log_handler = logging.basicConfig(level=logging.INFO)

client = discord.Client(intents=intents, log_handler=log_handler)
channel = None

# save a copy of the log to the install directory if we get this far
shutil.copyfile(log_file, os.path.join(install_dir, 'previous_log.txt'))

# bot: initialization
@client.event
async def on_ready():
    global channel
    channel = client.get_channel(discord_channel_id)
    if channel:
        try:
            txt = f'**Gentoo-Auto-Update:**\n```{packages}```'
            if len(txt) < 2000:
                await channel.send(txt, file=discord.File(log_file))
            else:
                await channel.send('**Gentoo-Auto-Update:**\nsee log file...', file=discord.File(log_file))
        finally:
            await client.close()

# log in and run the discord bot
client.run(discord_bot_token)

# finally, power off the machine after a small delay
Shutdown()
