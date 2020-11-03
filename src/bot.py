import os, urllib, json, sys, string, csv, datetime
from random import choice, randrange
import discord as discord_api
from discord.ext import commands
import inspect
import youtube
from dang_error import DangError
from helpers import debug_print, random_datetime_in_range, env

DISCORD_TOKEN = env('DISCORD_TOKEN')
DISCORD_GUILD = env('DISCORD_GUILD')
QUOTES_FILE = env('QUOTES_FILE')

channel_id = "UCQoNoTPf2FYSqM6c8sjXSZg"
first_upload_date = datetime.datetime(2016, 5, 1)

bot = commands.Bot(command_prefix='!')

# @bot.command(name='wakker')
# async def nine_nine(ctx):
#     debug_print('aaa')
#     await ctx.send('bruh')

def get_random_quote():
	poetic_quotes = []
	with open(QUOTES_FILE, newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter='|', quotechar='\\')
		for row in reader:
			poetic_quotes.append(row[0])
	return choice(poetic_quotes)

@bot.command(name='mooi')
async def send_quote(ctx):
    await ctx.send(get_random_quote())

@bot.command(name='latest')
async def send_latest_upload_url(ctx):
	items = youtube.search({
		'channelId': channel_id,
		'maxResults': '1',
		'order': 'date'
	})
	item = items[0]
	video_id = item['id']['videoId']
	await ctx.send("https://www.youtube.com/watch?v=" + video_id)

@bot.command(name='zoek')
async def search(ctx, *params):
	if len(params) == 0:
		debug_print("search without params, aborting..")
		return

	items = youtube.search({
		'q': ' '.join(params),
		'maxResults': '1',
	})
	item = items[0]
	video_id = item['id']['videoId']
	await ctx.send("https://www.youtube.com/watch?v=" + video_id)

@bot.command(name='random')
async def send_random(ctx, param = None):
	search_params = {
		'maxResults': '50'
	}
	
	if not param:
		#get from channel
		random_date = random_datetime_in_range(
			first_upload_date, 
			datetime.datetime.now()
		).isoformat() + 'Z'

		search_params['channelId'] = channel_id
		search_params['publishedAfter'] = random_date
	
	elif param == 'echt':
		#get anything from youtube
		random_date = random_datetime_in_range(
			datetime.datetime(2005, 4, 1), 
			datetime.datetime.now()
		).isoformat() + 'Z'
		
		random_string = ''.join(choice(string.ascii_lowercase) for i in range(3))

		search_params['publishedAfter'] = random_date
		search_params['q'] = random_string
	
	else:
		debug_print("Unknown param for search: " + param)
		return

	items = youtube.search(search_params)
	video_id = choice(items)['id']['videoId']
	await ctx.send("https://www.youtube.com/watch?v=" + video_id)


@bot.event
async def on_ready():
	print(get_random_quote())
	
	# try:
	# 	debug_print(get_true_random_upload_url())
	# except DangError as e:
	# 	debug_print(e.args[0])

	# for emoji in guild.emojis:
	# 	print(str(emoji))

	for guild in bot.guilds:
		if guild.name == DISCORD_GUILD:
			break

	print(
		f'{bot.user} is connected to the following guild:\n'
		f'{guild.name}(id: {guild.id})'
	)

# @bot.event
# async def on_message(message):
# 	if(message.author.bot):
# 		return

# 	debug_print("message received: " + message.content)

# 	elif randrange(0, 40) == 5:
# 		await message.channel.send(get_random_quote())


bot.run(DISCORD_TOKEN)