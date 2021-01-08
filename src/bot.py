import os, json, sys, string, csv, datetime
from dotenv import load_dotenv
from random import choice, randrange
import discord as discord_api
from discord.ext import commands
import inspect
from youtube import Youtube, YoutubeChannel
from youtube_s import Youtube_S
from dang_error import DangError
from helpers import debug_print, parse_str_emoji, get_text, get_emoji, get_config, guild_to_config_path, config_files_to_env

load_dotenv()
config_files_to_env()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!', help_command=None)
bot.add_cog(Youtube(bot))
bot.add_cog(Youtube_S(bot))

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

@bot.command(name='mooi',  description="An inspirational quote.")
async def send_quote(ctx):
	await ctx.send(get_random_quote(ctx.guild))

@bot.command(name="help", description="Shows this message.")
async def help(ctx):
	helptext = "```"
	for command in bot.commands:
		description = "|".join(command.aliases) if len(command.aliases) else command.name
		description += f": {command.description}"
		helptext+=f"{description}\n"
	helptext+="```"
	await ctx.send(helptext)

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
		raise error

@bot.event
async def on_ready():
	test_json_key = "config_"+os.getenv("TEST_GUILD_ID")
	print(test_json_key)


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

	#debug_print(message.author.id)
	debug_print("message received, " + str(message.author) + ": " + message.content)

	if ('<@!%s>' % bot.user.id) in message.content or ('<@%s>' % bot.user.id) in message.content:
		await message.channel.send(magic_eight_ball(message.guild))

	elif should_send_random_message(message.guild):
		await message.channel.send(get_random_quote(message.guild))

	await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
