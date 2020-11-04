import sys, os, string, datetime
from random import choice
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from discord.ext import commands
from helpers import debug_print, env, random_datetime_in_range
from dang_error import DangError

class Youtube(commands.Cog):
	youtube_api = None

	def __init__(self, bot, defaul_channel_dict):
		self.bot = bot
		self.default_channel = defaul_channel_dict

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
		
		if len(items) == 0:
			raise DangError('ik kan niks vinden')

		if all_pages and num_expected != len(items):
			debug_print("Only got " + str(len(items)) + " of " + str(num_expected) + "videos?")

		return items

	@commands.command(name='latest', pass_context=True)
	async def send_latest_upload_url(self, ctx):
		items = self.search({
			'channelId': self.default_channel['id'],
			'maxResults': '1',
			'order': 'date',
			'type': 'video'
		})
		item = items[0]
		video_id = item['id']['videoId']
		await ctx.send("https://www.youtube.com/watch?v=" + video_id)

	@commands.command(name='zoek', pass_context=True)
	async def send_search_result(self, ctx, *params):
		if len(params) == 0:
			debug_print("search without params, aborting..")
			return

		items = self.search({
			'q': ' '.join(params),
			'maxResults': '1',
			'type': 'video'
		})
		item = items[0]
		video_id = item['id']['videoId']
		await ctx.send("https://www.youtube.com/watch?v=" + video_id)

	@commands.command(name='random', pass_context=True)
	async def send_random(self, ctx, param = None):
		search_params = {
			'maxResults': '50',
			'type': 'video'
		}
		
		if not param:
			#get from channel
			random_date = random_datetime_in_range(
				self.default_channel['first_upload_date'], 
				datetime.datetime.now()
			).isoformat() + 'Z'

			search_params['channelId'] = self.default_channel['id']
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

		items = self.search(search_params)
		video_id = choice(items)['id']['videoId']
		await ctx.send("https://www.youtube.com/watch?v=" + video_id)