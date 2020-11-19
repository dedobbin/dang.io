import os, json, sys, string, csv, datetime, re, argparse
from random import choice, randrange
import discord as discord_api
from discord.ext import commands
import inspect
from youtube import Youtube, YoutubeChannel
from dang_error import DangError
from helpers import debug_print, env, set_env_path, get_text

parser = argparse.ArgumentParser()
parser.add_argument('--env_file', '-e', help="path to .env file containing guild and paths", type= str)
args=parser.parse_args()

set_env_path(args.env_file if args.env_file else None)

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
		if emoji.name == name:
			return str(emoji)
	
	debug_print('couldn not find emoji ' + name)
	return ''

def get_random_message_freq():
	freq = env("RANDOM_MESSAGE_FREQ")
	return freq if freq else 61

def magic_eight_ball():
	return choice(get_text('magic_eight_ball'))

# Replace ___EMOJI_EMOJINAME___ with proper emoji, based on emoji_map
def parse_str_emoji(teh_string):
	
	p = re.compile(r"___EMOJI_[a-zA-Z0-9_]*___")
	for res in re.findall(p, teh_string):
		emoji = res.strip("___").lstrip("EMOJI_")
		teh_string = teh_string.replace(res, get_emoji(emoji))	
		
	return teh_string

@bot.command(name='mooi')
async def send_quote(ctx):
    await ctx.send(parse_str_emoji(get_random_quote()))

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandInvokeError) and isinstance(error.original, DangError):
		await ctx.send(parse_str_emoji(str(error.original)) + ' ' + get_emoji('cry'))
	else:
		debug_print(error)
		await ctx.send(parse_str_emoji(get_text("errors", "general")))
		raise error

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
		await message.channel.send(parse_str_emoji(magic_eight_ball()))

	elif randrange(0, get_random_message_freq()) == 1:
		await message.channel.send(parse_str_emoji(get_random_quote()))
		await message.channel.send(parse_str_emoji(get_text('happy')))

	await bot.process_commands(message)

bot.run(DISCORD_TOKEN)