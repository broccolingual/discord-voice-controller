import os
import logging
from pathlib import Path

from discord.ext import commands, tasks

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# StreamHandler作成
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(name)s:%(lineno)d:%(levelname)s:%(message)s'))
logger.addHandler(handler)

cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f'{cwd}\n----------------')

bot = commands.Bot(command_prefix='v/')
bot.remove_command('help')
bot.cwd = cwd


@bot.event
async def on_connect():
    logger.info('bot connected')


@bot.event
async def on_disconnect():
    logger.info('bot disconnected')


@bot.event
async def on_ready():
    logger.info(f'bot is ready, Logged in as {bot.user.name}')


if __name__ == '__main__':
    for file in os.listdir(cwd + '/cogs'):
        if file.endswith('.py') and not file.startswith('_'):
            bot.load_extension(f'cogs.{file[:-3]}')

bot.run('NzY0NTEwMDIxMzI5MDkyNjA5.X4HTcA.8ToRa95L2Jak4PqOWvj8PueM7Es')