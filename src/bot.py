import os, urllib, json, sys, string, csv
from random import randrange, uniform, choice
import discord as discord_api
from dotenv import load_dotenv
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import inspect

debug_bool = True

class DangError(Exception):
	def __init__(self, *args):
		self.args = [a for a in args]

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_GUILD = os.getenv('DISCORD_GUILD')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY');
YOUTUBE_SECRET_FILE = os.getenv('YOUTUBE_SECRETS_FILE')
QUOTES_FILE = os.getenv('QUOTES_FILE')

dang_channel_id = "UCQoNoTPf2FYSqM6c8sjXSZg"

def youtube_auth(oauth = False):
	# YOUTUBE_SECRET_FILE should be file with JSON obtained from https://console.developers.google.com/apis/credentials, OAuth 2.0-client-ID's 
	# YOUTUBE_API_KEY can also be obtained from there
	api_service_name = "youtube"
	api_version = "v3"

	if oauth:
		scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
		youtube_oath_flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(YOUTUBE_SECRET_FILE, scopes)
		credentials = youtube_oath_flow.run_console()
		youtube_api = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
	else:
		youtube_api = googleapiclient.discovery.build(api_service_name, api_version, developerKey=YOUTUBE_API_KEY)
	
	return youtube_api
		

youtube_api = youtube_auth()
discord_client = discord_api.Client()

def debug_print(input):
	if (debug_bool):
		if (isinstance(input, str)):
			print("<DEBUG> " + input)
		else:
			print("<DEBUG> ")
			print(input)

def search(dynamic_params, all_pages = False):
	static_params = {"part":"snippet"}

	params = {**static_params, **dynamic_params}

	num_expected = 0
	items = []
	try:
		request = youtube_api.search().list(**params)
		response = request.execute()
		items = response['items']

		num_expected = response['pageInfo']['totalResults']
		if (all_pages):
			try:
				next_page = response['nextPageToken']
				while True:
					request = youtube_api.search().list(
						part="snippet", 
						#channelId=channel_id,
						maxResults="50",
						pageToken=next_page
					)
					response = request.execute()
					items += response['items']
					next_page = response['nextPageToken']
			except KeyError as e:
				pass
	except googleapiclient.errors.HttpError as e:
		debug_print("Failed to connect to Youtube: " + getattr(e, 'message', repr(e)))
		raise DangError("ik heb geen verbinding met youtube :cry~1:")
	
	if all_pages and num_expected != len(items):
		debug_print("Only got " + str(len(items)) + " of " + str(num_expected) + "videos?")

	if len(items) == 0:
		raise DangError("ik kan geen videos vinden :cry~1:")

	return items

def get_uploads(params, all_pages = False):
	params ["channelId"] = dang_channel_id
	return search(params, all_pages = all_pages)

def get_all_uploads():
	return get_uploads({"maxResults":"50", "channelId" : dang_channel_id}, all_pages = True)

def get_latest_upload_url():
	items = get_uploads({"maxResults": "1", "order": "date"})
	video_id = items[0]['id']['videoId']
	return "https://www.youtube.com/watch?v=" + video_id

def get_random_upload_url():
	items = get_all_uploads()
	item = choice(items)
	video_id = item['id']['videoId']
	return "https://www.youtube.com/watch?v=" + video_id

def get_true_random_upload_url():
	s = ''.join(choice(string.ascii_lowercase) for i in range(10))
	#items = search({'q':s}, all_pages = True)
	items = search({'q':s}, all_pages = True)
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
	
	try:
		debug_print(get_random_upload_url())
	except DangError as e:
		debug_print(e.args[0])

	for guild in discord_client.guilds:
		if guild.name == DISCORD_GUILD:
			break

	print(
		f'{discord_client.user} is connected to the following guild:\n'
		f'{guild.name}(id: {guild.id})'
	)

@discord_client.event
async def on_message(message):
	if message.author == discord_api.Client().user:
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
