import sys, os, string, datetime, json
from random import choice, randrange
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from discord.ext import commands
from helpers import random_datetime_in_range, get_text, get_config, guild_to_config_path
from dang_error import DangError
import logging

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
		if len(self.result['items']) == 0:
			raise DangError("geen videos gevonden???")
		
		self.cursor = randrange(0, len(self.result['items']))
		return self.result['items'][self.cursor]

	def first_item(self):
		if len(self.result['items']) == 0:
			raise DangError("geen videos gevonden???")
		
		self.cursor = 0
		return self.result['items'][self.cursor]

	# Returns none if no next exists, so can get next page
	def next_item(self):		
		try:
			item = self.result['items'][self.cursor + 1]
			self.cursor += 1
			return item
		except KeyError as e:
			logging.warning('no next video in search result..')
			return None

	def get_next_page(self, search_callback):
		params = self.params
		params['pageToken'] = self.result['nextPageToken']
		result = search_callback(params)
		return result

class Youtube(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.youtube_api = None
		# Maps guild ID to a default youtube channel, defined in config/guild/youtube.json
		self.__default_channels = {}

		# maps search results to sent message ID after sending, so can look up when reaction on message comes in 
		self.video_messages = {}
		self.max_video_message_history = 10
		try:
			self.youtube_auth()
		except Exception as e:
			logging.error("Failed to connect to youtube " + str(e))

	def youtube_auth(self, oauth = False):
		api_service_name = "youtube"
		api_version = "v3"

		# YOUTUBE_SECRET_FILE should be file with JSON obtained from https://console.developers.google.com/apis/credentials, OAuth 2.0-client-ID's 
		# YOUTUBE_API_KEY can also be obtained from there
		YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY');
		YOUTUBE_SECRET_FILE = os.getenv('YOUTUBE_SECRETS_FILE')

		if oauth:
			scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
			youtube_oath_flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(YOUTUBE_SECRET_FILE, scopes)
			credentials = youtube_oath_flow.run_console()
			self.youtube_api = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
		else:
			self.youtube_api = googleapiclient.discovery.build(api_service_name, api_version, developerKey=YOUTUBE_API_KEY)
	
	def get_default_channel(self, guild):
		try:
			return self.__default_channels[guild.id]
		except KeyError:
				data = get_config(guild.id, "youtube_default_channel")
				if not data:
					return None
				# TODO: get first upload date automagically, oh this seems not possible through youtube api
				y, m, d = data['first_upload_date'].split('-')

				first_upload_date = datetime.datetime(int(y), int(m), int(d))
				self.__default_channels[guild.id] = YoutubeChannel(data['id'], first_upload_date)
				return self.__default_channels[guild.id]

	# Adds search result to history + returns index key of entry in history
	def search(self, dynamic_params, all_pages = False, guild = None):
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
			logging.error("Failed to connect to Youtube: " + getattr(e, 'message', repr(e)))
			raise DangError(get_text('errors', 'youtube', guild = guild))

		if all_pages and num_expected != len(items):
			logging.warning("Only got " + str(len(items)) + " of " + str(num_expected) + "videos?")

		#self.search_results.append({'result': response, 'params': params})

		if len(items) == 0:
			raise DangError(get_text('errors', 'no_videos', guild = guild))

		return SearchResult(response, params)

	
	################# send-commands #################

	@commands.command(name='latest', pass_context=True,  description="Sends latest upload from default channel.")
	async def send_latest_upload_url(self, ctx):
		youtube_channel = self.get_default_channel(ctx.guild) 
		search_params = {
			'channelId': youtube_channel.id,
			'maxResults': '25',
			'order': 'date',
			'type': 'video'
		}

		result = self.search(search_params, guild = ctx.guild)
		item = result.first_item()
		await self.send_video(ctx.message.channel, item, result)

	@commands.command(aliases=['search', 'zoek'], pass_context=True, description="Standard Youtube search. Param is search query.")
	async def send_search_result(self, ctx, *params):
		if len(params) == 0:
			logging.warning("search without params, aborting.." + "(" + ctx.guild.name + ")")
			return

		search_params = {
			'q': ' '.join(params),
			'maxResults': '25',
			'type': 'video'
		}

		result = self.search(search_params, guild = ctx.guild)
		item = result.first_item()
		await self.send_video(ctx.message.channel, item, result)

	@commands.command(aliases=['random', 'willekeurig'], pass_context=True,  description="Send a random video. Use param 'default' to get from default channel.")
	async def send_random(self, ctx, param = None):
		search_params = {
			'maxResults': '50',
			'type': 'video'
		}
		
		if not param:
			#get anything from youtube
			random_date = random_datetime_in_range(
				datetime.datetime(2005, 4, 1), 
				datetime.datetime.now()
			).isoformat() + 'Z'
			
			random_string = ''.join(choice(string.ascii_lowercase) for i in range(3))

			search_params['publishedAfter'] = random_date
			search_params['q'] = random_string
		
		elif param == 'default':
			#get from channel
			youtube_channel = self.get_default_channel(ctx.guild) 
			random_date = random_datetime_in_range(
				youtube_channel.first_upload_datetime, 
				datetime.datetime.now()
			).isoformat() + 'Z'

			search_params['channelId'] = youtube_channel.id
			search_params['publishedAfter'] = random_date
		
		else:
			logging.error("Unknown param for search: " + param)
			return

		result = self.search(search_params, guild = ctx.guild)
		item = result.random_item()
		await self.send_video(ctx, item, result)

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		#TODO: video_id_to_url
		#TODO: when searched random, get a new random result instead of next???
		try:
			if '👎' in str(reaction):
				associated_search_result = self.video_messages[reaction.message.id]
				# TODO: if random video was searched, random random one instead of next

				await reaction.message.channel.send(get_text(reaction.message.guild.id, "next_video"))
				next_video = associated_search_result.next_item()
				if not next_video:
					associated_search_result = associated_search_result.get_next_page(self.search)
					next_video = associated_search_result.first_item()
				await self.send_video(reaction.message.channel, next_video, associated_search_result)

		except KeyError as e:
			pass

	#Pass search_result so can map sent message id to search_result, to use on reactions
	async def send_video(self, channel, item, search_result = None):
		video_id = item['id']['videoId']
		message = await channel.send('https://www.youtube.com/watch?v=' + video_id)

		if search_result:
			if len(self.video_messages) >= self.max_video_message_history:
				# key 0 is lowest message ID, so oldest, remove that one..
				del self.video_messages[list(self.video_messages.keys())[0]]
			self.video_messages[message.id] = search_result
