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
last_video_message_sent = None

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

@bot.event
async def on_command_error(ctx, error):
    debug_print(error)
    if isinstance(error, commands.CommandInvokeError) and isinstance(error.original, DangError):
        await ctx.send(str(error.original) + ' ' + get_emoji('cry'))
    else:
        await ctx.send('er is iets niet goed gegaan ' + get_emoji('cry'))

@bot.event
async def on_reaction_add(reaction, user):
	global last_video_message_sent
	
	if reaction.message.id == last_video_message_sent.id:
		if '👎' in str(reaction):
			await reaction.message.channel.send('sorry, ik zal de volgende sturen ' + get_emoji('uh'))
			#TODO: place function in youtube module
			#TODO: actually iterate instead of static 1
			#TODO: instead of key error, check if there is another result
			#TODO: test next page
			#TODO: check if there is a next page
			#TODO: when searched random, get a new random result instead of next???
			#TODO: video_id_to_url
			yt = bot.get_cog('Youtube')
			try:
				video_id = yt.last_search_result['result']['items'][1]['id']['videoId']
			except KeyError as e:
				next_page_token = yt.last_search_result['result']['nextPageToken']
				video_id = yt.search({**yt.yt.last_search_result['params'], 'nextPageToken': next_page_token})[0]
			await reaction.message.channel.send('https://www.youtube.com/watch?v=' + video_id)

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
	global last_video_message_sent
	
	if(message.author.bot):
		if 'www.youtube.com' in message.content:
			last_video_message_sent = message
			debug_print('last video message id: ' + str(message.id))
		return

	debug_print("message received: " + message.content)


	if ('<@!%s>' % bot.user.id) in message.content or ('<@%s>' % bot.user.id) in message.content:
		await message.channel.send(get_emoji('dangs_up2'))

	elif randrange(0, 60) == 5:
		await message.channel.send(get_random_quote())
		await message.channel.send(get_emoji('dangs_up2'))

	await bot.process_commands(message)

bot.run(DISCORD_TOKEN)