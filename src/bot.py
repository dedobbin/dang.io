import os, json, sys, string, csv, datetime, re
from random import choice, randrange
import discord as discord_api
from discord.ext import commands
import inspect
from youtube import Youtube, YoutubeChannel
from dang_error import DangError
from helpers import debug_print, env

DISCORD_TOKEN = env('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!', help_command=None)
bot.add_cog(Youtube(bot))

texts = {}

def get_random_quote(guild):
	poetic_quotes = []
	with open('config/' + str(guild.id) + '/quotes.csv', newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter='|', quotechar='\\')
		for row in reader:
			poetic_quotes.append(row[0])
	return choice(poetic_quotes)

def get_emoji(name, guild):
	for emoji in guild.emojis:
		if emoji.name == name:
			return str(emoji)
	
	debug_print('couldn not find emoji ' + name)
	return ''

def get_text(*args, guild=None):
	global texts
	try:
		guild_texts = texts[guild.id]
	except KeyError as e:
		with open('config/' + str(guild.id) + '/texts.json') as f:
			texts[guild.id] = json.load(f)
			guild_texts = texts[guild.id]

	if len(args) == 0:
		raise (ValueError("get_text called without params"))

	result = ""
	try:
		result = guild_texts[args[0]]
		
		for i in range(1, len(args)):
			result = result[args[i]]
	except KeyError as e:
		print("text not found, keys: " + str(args))
		return ""

	return result

def get_random_message_freq():
	freq = env("RANDOM_MESSAGE_FREQ")
	return int(freq) if freq else 61

def magic_eight_ball(guild):
	return choice(get_text('magic_eight_ball', guild=guild))

# Replace ___EMOJI_EMOJINAME___ with proper emoji, based on emoji_map
def parse_str_emoji(teh_string, guild):
	
	p = re.compile(r"___EMOJI_[a-zA-Z0-9_]*___")
	for res in re.findall(p, teh_string):
		emoji = res.strip("___").lstrip("EMOJI_")
		teh_string = teh_string.replace(res, get_emoji(emoji, guild))	
		
	return teh_string

@bot.command(name='mooi')
async def send_quote(ctx):
    await ctx.send(parse_str_emoji(get_random_quote(ctx.guild), ctx.guild))

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandInvokeError) and isinstance(error.original, DangError):
		await ctx.send(parse_str_emoji(str(error.original), ctx.guild) + ' ' + get_emoji('cry', ctx.guild))
	else:
		debug_print(error)
		await ctx.send(parse_str_emoji(get_text("errors", "general", guild=ctx.guild), ctx.guild))
		raise error

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
		# test stuff
		await message.channel.send(parse_str_emoji(magic_eight_ball(message.guild), message.guild))

	elif randrange(0, get_random_message_freq()) == 1:
		await message.channel.send(parse_str_emoji(get_random_quote(message.guild)))
		await message.channel.send(parse_str_emoji(get_text('happy', message.guild)))

	await bot.process_commands(message)

bot.run(DISCORD_TOKEN)