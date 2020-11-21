import os, json, sys, string, csv, datetime
from dotenv import load_dotenv
from random import choice, randrange
import discord as discord_api
from discord.ext import commands
import inspect
from youtube import Youtube, YoutubeChannel
from dang_error import DangError
from helpers import debug_print, config_file_path, parse_str_emoji, get_text, get_emoji

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!', help_command=None)
bot.add_cog(Youtube(bot))

def get_random_quote(guild):
	poetic_quotes = []
	with open(config_file_path('quotes.csv', guild), newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter='|', quotechar='\\')
		for row in reader:
			poetic_quotes.append(row[0])
	return parse_str_emoji(choice(poetic_quotes), guild)

def get_random_message_freq():
	freq = os.getenv("RANDOM_MESSAGE_FREQ")
	return int(freq) if freq else 61

def magic_eight_ball(guild):
	return choice(get_text('magic_eight_ball', guild = guild))

@bot.command(name='mooi')
async def send_quote(ctx):
    await ctx.send(get_random_quote(ctx.guild))

@bot.event
async def on_command_error(ctx, error):
	#debug_print(error)
	if isinstance(error, commands.CommandInvokeError) and isinstance(error.original, DangError):
		debug_print("Dang error: " + str(error))
		await ctx.send(parse_str_emoji(str(error.original), ctx.guild))
	elif isinstance(error, commands.CommandNotFound):
		# Don't respond to unknown commands
		debug_print(str(error))
	else:
		debug_print("General error: " + str(error))
		await ctx.send(get_text("errors", "general", guild = ctx.guild))

@bot.event
async def on_ready():
	print('Went online in')
	for g in bot.guilds:
		print(g.name + '(' + str(g.id) + ')')

	#test stuff
	debug_print(get_text('errors', 'youtube'))
	#debug_print(guild.emojis)

@bot.event
async def on_message(message):
	if(message.author.bot):
		if 'www.youtube.com' in message.content:
			debug_print('sent video')
		return

	debug_print("message received: " + message.content)

	if ('<@!%s>' % bot.user.id) in message.content or ('<@%s>' % bot.user.id) in message.content:
		await message.channel.send(magic_eight_ball(message.guild))

	elif randrange(0, get_random_message_freq()) == 1:
		await message.channel.send(get_random_quote(message.guild))

	await bot.process_commands(message)

bot.run(DISCORD_TOKEN)