import os, json, sys, string, csv, datetime
from dotenv import load_dotenv
from random import choice, randrange
import discord as discord_api
from discord.ext import commands
import inspect
from youtube import Youtube, YoutubeChannel
from dang_error import DangError
from helpers import debug_print, parse_str_emoji, get_text, get_emoji, get_config, guild_to_config_path

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!', help_command=None)
bot.add_cog(Youtube(bot))

def get_random_quote(guild):
	return choice(get_text("quotes", guild = guild))

def magic_eight_ball(guild):
	return choice(get_text('magic_eight_ball', guild = guild))

def should_send_random_message(guild = None):
	#TODO: cache freq
	freq = get_config("spam_freq", config_folder = guild_to_config_path(guild))
	if (freq <= 0):
		return False
	c = randrange(0, freq )
	return c == 0

@bot.command(name='mooi')
async def send_quote(ctx):
	await ctx.send(get_random_quote(ctx.guild))

# TODO: also handle errors in events
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

	elif should_send_random_message(message.guild):
		await message.channel.send(get_random_quote(message.guild))

	await bot.process_commands(message)

bot.run(DISCORD_TOKEN)