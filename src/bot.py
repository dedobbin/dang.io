import os, urllib, json, sys, string, csv, datetime
from random import choice, randrange
import discord as discord_api
import inspect
import youtube
from dang_error import DangError
from helpers import debug_print, random_datetime_in_range, env



DISCORD_TOKEN = env('DISCORD_TOKEN')
DISCORD_GUILD = env('DISCORD_GUILD')
QUOTES_FILE = env('QUOTES_FILE')

dang_channel_id = "UCQoNoTPf2FYSqM6c8sjXSZg"
first_upload_date = datetime.datetime(2016, 5, 1)

discord_client = discord_api.Client()

def get_uploads(params, all_pages = False):
	params ["channelId"] = dang_channel_id
	return youtube.search(params, all_pages = all_pages)

def get_latest_upload_url():
	items = get_uploads({"maxResults": "1", "order": "date"})
	video_id = items[0]['id']['videoId']
	return "https://www.youtube.com/watch?v=" + video_id

def get_random_upload_url():
	random_date = random_datetime_in_range(first_upload_date, datetime.datetime.now())
	items = get_uploads({
		'publishedAfter': random_date.isoformat() + 'Z',
		"maxResults": "50"
	})
	item = choice(items)
	video_id = item['id']['videoId']
	return "https://www.youtube.com/watch?v=" + video_id

def get_all_uploads():
	return get_uploads({"maxResults":"50", "channelId" : dang_channel_id}, all_pages = True)

def get_true_random_upload_url():
	s = ''.join(choice(string.ascii_lowercase) for i in range(10))
	random_date = random_datetime_in_range(first_upload_date, datetime.datetime.now())

	items = youtube.search({
		'q':s,
		'publishedAfter': random_date.isoformat() + 'Z',
		"maxResults": "50"
	})

	item = choice(items)
	video_id = item['id']['videoId']
	return "https://www.youtube.com/watch?v=" + video_id

def get_random_quote():
	poetic_quotes = []
	with open(QUOTES_FILE, newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter='|', quotechar='\\')
		for row in reader:
			poetic_quotes.append(row[0])
	return choice(poetic_quotes)


commands =  {
	'latest' : get_latest_upload_url,
	'random' : get_random_upload_url,
	'echt random' : get_true_random_upload_url,
	'mooi' : get_random_quote 
}

@discord_client.event
async def on_ready():
	print(get_random_quote())
	
	# try:
	# 	debug_print(get_true_random_upload_url())
	# except DangError as e:
	# 	debug_print(e.args[0])

	for guild in discord_client.guilds:
		if guild.name == DISCORD_GUILD:
			break

	# for emoji in guild.emojis:
	# 	print(str(emoji))
	
	print(
		f'{discord_client.user} is connected to the following guild:\n'
		f'{guild.name}(id: {guild.id})'
	)

@discord_client.event
async def on_message(message):
	if(message.author.bot):
		return

	debug_print("message received: " + message.content)

	#When developer tags, the tag contains a '!'? unsure why
	if ('<@!%s>' % discord_client.user.id) in message.content or ('<@%s>' % discord_client.user.id) in message.content:
		debug_print("checking commands..")
		try:
			for key, value in commands.items():
				if key in message.content:
					debug_print("found found: " + key)
					text = value()
					await message.channel.send(text)
					break
		
		except DangError as e:
			await message.channel.send(e.args[0])

	elif randrange(0, 40) == 5:
		await message.channel.send(get_random_quote())


discord_client.run(DISCORD_TOKEN)
