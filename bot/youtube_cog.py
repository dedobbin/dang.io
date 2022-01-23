import string, datetime, logging
from random import choice
from discord.ext import commands
import config
from helpers import random_datetime_in_range
from youtube import Youtube, YoutubeChannel
class YoutubeCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.youtube = Youtube()

		# maps search results to sent message ID after sending, so can look up when reaction on message comes in 
		self.video_messages = {}
		self.max_video_message_history = 10

	@commands.command(name='latest', pass_context=True,  description="Sends latest upload from default channel. React with 'thumbs down' for next video.")
	async def send_latest_upload_url(self, ctx):
		youtube_channel = self.get_default_channel(ctx.guild) 
		
		if not youtube_channel:
			logging.warning("Requested latest upload but no default channel (" + ctx.guild.name + ")")
			raise commands.CommandNotFound("Command not found, latest")

		search_params = {
			'channelId': youtube_channel.id,
			'maxResults': '25',
			'order': 'date',
			'type': 'video'
		}

		result = self.youtube.search(search_params, guild = ctx.guild)
		item = result.first_item()
		await self.send_video(ctx.message.channel, item, result)

	@commands.command(aliases=['search', 'zoek'], pass_context=True, description="Standard Youtube search. Param is search query.")
	async def send_search_result(self, ctx, *params):
		if len(params) == 0:
			logging.warning("search without params, aborting.." + "(" + ctx.guild.name + ")")
			await ctx.send(config.get_error_text(ctx.guild.id, "no_param_search"))
			return

		search_params = {
			'q': ' '.join(params),
			'maxResults': '25',
			'type': 'video'
		}

		result = self.youtube.search(search_params, guild = ctx.guild)
		item = result.first_item()
		await self.send_video(ctx.message.channel, item, result)

	@commands.command(aliases=['random', 'willekeurig'], pass_context=True,  description="Send a random video. React with 'thumbs down' for next video. When a default channel is set, use param 'default' to get from this channel.")
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
		
		elif param == 'default' and self.get_default_channel(ctx.guild):
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

		result = self.youtube.search(search_params, guild = ctx.guild)
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

				await reaction.message.channel.send(config.get_text(reaction.message.guild.id, "next_video"))
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

	def get_default_channel(self, guild):
		data = config.get_config(guild.id, "youtube_default_channel")
		if not data:
			return None
		# TODO: get first upload date automagically, oh this seems not possible through youtube api
		y, m, d = data['first_upload_date'].split('-')

		first_upload_date = datetime.datetime(int(y), int(m), int(d))
		return YoutubeChannel(data['id'], first_upload_date)