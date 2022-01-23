from time import sleep, time
from discord.ext import commands
import os
from config import get_text, get_error_text
from dang_error import DangError
from random import choice
import logging
from youtube_s import Youtube_S

class Youtube_S_Cog(commands.Cog):
	def __init__(self, bot):
		fastMode = os.getenv("YOUTUBE_S_FAST_MODE")
		try:
			self.youtube_s = Youtube_S(fastMode)
		except Exception as e:
			#logging.error(f"Could not start Youtube_S: {e}")
			self.youtube_s = None
			pass
		self.bot = bot

	@commands.command(aliases=['obscure', 'obscuur'], pass_context=True,  description="Sends a random obscure video. Parameter is search query (optional).\n\nSuccess rate depends on time of day. Also because of the janky nature of this command, using no parameter might cause no video to be find. Just try again!")
	async def s_latest(self, ctx, *params):
		if not self.youtube_s:
			logging.error(ctx.guild.name + " tried to use youtube_s, but it didn't come up on startup")
			raise DangError(get_error_text(ctx.guild.id, "youtube_s"))
		
		start_time = time()

		async with ctx.typing():
			items = self.youtube_s.get_obscure_videos(*params)

		logging.info("Youtube_s took %s seconds" % (time() - start_time))

		message = ""
		if len(items) == 0 and len(params) > 0:
			#No videos found with search term, try again without it as fallback
			items = self.youtube_s.get_obscure_videos()
			message = get_text(ctx.guild.id, "youtube_s_fallback")
		
		if len(items) == 0:
			raise DangError(get_error_text(ctx.guild.id, "no_videos_try_again"))

		await ctx.send(message + choice(items)["url"])				
