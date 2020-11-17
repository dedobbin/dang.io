import os, json, sys, string, csv, datetime
from random import choice, randrange
import discord as discord_api
from discord.ext import commands
import inspect
from youtube import Youtube, YoutubeChannel
from dang_error import DangError
from helpers import debug_print, env

DISCORD_TOKEN = env('DISCORD_TOKEN')
DISCORD_GUILD = env('DISCORD_GUILD')
QUOTES_FILE = env('QUOTES_FILE')


d,m,y = env('DEFAULT_CHANNEL_FIRST_UPLOAD_DATE').split('-')
first_upload_date = datetime.datetime(int(d), int(m), int(y))
default_channel = YoutubeChannel(env('DEFAULT_CHANNEL_ID'),first_upload_date)

bot = commands.Bot(command_prefix='!')
bot.add_cog(Youtube(bot, default_channel))
guild = None

def get_random_quote():
	poetic_quotes = []
	with open(QUOTES_FILE, newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter='|', quotechar='\\')
		for row in reader:
			poetic_quotes.append(row[0])
	return choice(poetic_quotes)

def get_emoji(name):
	for emoji in guild.emojis:
		#emojis[emoji.name] = str(emoji)
		if emoji.name == name:
			return str(emoji)
	
	debug_print('couldn not find emoji ' + name)
	return ''

@bot.command(name='mooi')
async def send_quote(ctx):
    await ctx.send(get_random_quote())

# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.CommandInvokeError) and isinstance(error.original, DangError):
#         await ctx.send(str(error.original) + ' ' + get_emoji('cry'))
#     else:
#         await ctx.send('er is iets niet goed gegaan ' + get_emoji('cry'))
# 		# TODO: raise

@bot.event
async def on_ready():
	global guild

	print(get_random_quote())

	for guild in bot.guilds:
		if guild.name == DISCORD_GUILD:
			break

	print(
		f'{bot.user} is connected to the following guild:\n'
		f'{guild.name}(id: {guild.id})'
	)

@bot.event
async def on_message(message):
	if(message.author.bot):
		if 'www.youtube.com' in message.content:
			debug_print('sent video')
		return

	debug_print("message received: " + message.content)


	if ('<@!%s>' % bot.user.id) in message.content or ('<@%s>' % bot.user.id) in message.content:
		await message.channel.send(get_emoji('dangs_up2'))

	elif randrange(0, 60) == 5:
		await message.channel.send(get_random_quote())
		await message.channel.send(get_emoji('dangs_up2'))

	await bot.process_commands(message)

bot.run(DISCORD_TOKEN)