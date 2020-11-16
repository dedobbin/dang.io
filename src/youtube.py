import sys, os, string, datetime
from random import choice, randrange
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from discord.ext import commands
from helpers import debug_print, env, random_datetime_in_range
from dang_error import DangError

class YoutubeChannel:
	def __init__(self, id, first_upload_datetime = datetime.datetime(2005, 4, 1)):
		self.id = id
		self.first_upload_datetime = first_upload_datetime

class SearchResult:
	def __init__(self, result, params):
		self.params = params
		self.result = result
		
		# points to last accessed item, so can get next etc
		self.cursor = None

	def random_item(self):
		self.cursor = randrange(0, len(self.result['items']))
		return self.result['items'][self.cursor]

	def first_item(self):
		self.cursor = 0
		return self.result['items'][self.cursor]

	def next_item(self, search_callback):
		self.cursor += 1
		try:
			raise KeyError
			item = self.result['items'][self.cursor]
		except KeyError as e:
			#TODO: handle if no next page
			self.params['pageToken'] = self.result['nextPageToken']
			self.result = search_callback(self.params).result
			item = self.first_item()

		return item

class Youtube(commands.Cog):
	def __init__(self, bot, default_channel):
		self.bot = bot
		self.default_channel  = default_channel
		self.youtube_api = None

		# maps search results to sent message ID after sending, so can look up when reaction on message comes in 
		self.video_messages = {}

	def youtube_auth(self, oauth = False):
		api_service_name = "youtube"
		api_version = "v3"

		# YOUTUBE_SECRET_FILE should be file with JSON obtained from https://console.developers.google.com/apis/credentials, OAuth 2.0-client-ID's 
		# YOUTUBE_API_KEY can also be obtained from there
		YOUTUBE_API_KEY = env('YOUTUBE_API_KEY');
		YOUTUBE_SECRET_FILE = env('YOUTUBE_SECRETS_FILE')

		if oauth:
			scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
			youtube_oath_flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(YOUTUBE_SECRET_FILE, scopes)
			credentials = youtube_oath_flow.run_console()
			self.youtube_api = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
		else:
			self.youtube_api = googleapiclient.discovery.build(api_service_name, api_version, developerKey=YOUTUBE_API_KEY)
	
	# Adds search result to history + returns index key of entry in history
	def search(self, dynamic_params, all_pages = False):
		if self.youtube_api == None:
			self.youtube_auth()

		static_params = {"part":"snippet"}

		params = {**static_params, **dynamic_params}

		num_expected = 0
		items = []
		try:
			request = self.youtube_api.search().list(**params)
			response = request.execute()
			items = response['items']

			num_expected = response['pageInfo']['totalResults']
			if (all_pages):
				try:
					next_page = response['nextPageToken']
					while True:
						request = self.youtube_api.search().list(
							part="snippet", 
							#channelId=default_flavor['id'],
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
			raise DangError('ik heb geen verbinding met youtube')

		if all_pages and num_expected != len(items):
			debug_print("Only got " + str(len(items)) + " of " + str(num_expected) + "videos?")

		#self.search_results.append({'result': response, 'params': params})
		
		if len(items) == 0:
			raise DangError('ik kan niks vinden')

		return SearchResult(response, params)

	
	################# send functions #################

	@commands.command(name='latest', pass_context=True)
	async def send_latest_upload_url(self, ctx):
		search_params = {
			'channelId': self.default_channel.id,
			'maxResults': '25',
			'order': 'date',
			'type': 'video'
		}

		result = self.search(search_params)
		item = result.first_item()
		await self.send_video(ctx.message.channel, item, result)

	@commands.command(name='zoek', pass_context=True)
	async def send_search_result(self, ctx, *params):
		if len(params) == 0:
			debug_print("search without params, aborting..")
			return

		search_params = {
			'q': ' '.join(params),
			'maxResults': '25',
			'type': 'video'
		}

		result = self.search(search_params)
		item = result.first_item()
		await self.send_video(ctx.message.channel, item, result)

	@commands.command(name='random', pass_context=True)
	async def send_random(self, ctx, param = None):
		search_params = {
			'maxResults': '50',
			'type': 'video'
		}
		
		if not param:
			#get from channel
			random_date = random_datetime_in_range(
				self.default_channel.first_upload_datetime, 
				datetime.datetime.now()
			).isoformat() + 'Z'

			search_params['channelId'] = self.default_channel.id
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

		result = self.search(search_params)
		item = result.random_item()
		await self.send_video(ctx, item, result)

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		#TODO: video_id_to_url
		#TODO: when searched random, get a new random result instead of next???
		
		#debug_print("got reaction: " + str(reaction))
		try:
			if '👎' in str(reaction):
				associated_search_result = self.video_messages[reaction.message.id]
				await reaction.message.channel.send('sorry, ik zal de volgende sturen')
				next_video = associated_search_result.next_item(self.search)
				await self.send_video(reaction.message.channel, next_video, associated_search_result)

		except KeyError as e:
			pass

	#Pass search_result so can map sent message id to search_result, to use on reactions
	async def send_video(self, channel, item, search_result = None):
		video_id = item['id']['videoId']
		message = await channel.send('https://www.youtube.com/watch?v=' + video_id)
		
		if search_result:
			self.video_messages[message.id] = search_result