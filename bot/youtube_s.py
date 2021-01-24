from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
# from bs4 import BeautifulSoup
# import requests
from time import sleep, time
from discord.ext import commands
import string, os
from helpers import get_text, get_error_text
from dang_error import DangError
from random import choice
import logging

########### youtube doesn't like bots, and they increase view count, which is against TOS, so use at own risk

class Youtube_S(commands.Cog):
	param_last_hour = {"sp" : "EgQIARAB"}
	fast_mode = os.getenv("YOUTUBE_S_FAST_MODE")

	def __init__(self, bot):
		option = webdriver.ChromeOptions()
		if not os.getenv("DEBUG_MODE"):
			option.add_argument("--headless")
			option.add_argument('--disable-gpu')
		try:
			self.driver = webdriver.Chrome(executable_path=os.getenv('CHROME_EXECUTABLE_PATH'), options=option)
		except Exception as e:
			logging.error("couldn't start web driver:" +  str(e))
		self.bot = bot


	def scroll_to_bottom(self):
		# pretty jank, but works usually 
		# TODO: finetune for faster responses, don't need all results
		body = self.driver.find_element_by_css_selector("body")
		for i in range (0, 100):
			body.send_keys(Keys.PAGE_DOWN)
		return

	def create_url(self, params):
		url = "https://www.youtube.com/results"

		if len(params) > 0:
			url += "?"
			for key in params:
				url+= key + "=" + params[key] + "&"
			url =  url.rstrip("&")
		
		return url

	def parse_views_html(self, inner_html):
		if "K" in inner_html:
			# uh..
			res = (inner_html.replace("K", "000") if not "." in inner_html else inner_html.replace(".", "") + "00").replace("K", "").replace(" ", "")
		else:
			res = inner_html.replace("No", "0")

		res = int(''.join(filter(str.isdigit, res)))
	
		return res

	def get_videos(self, params, guild = None):
		self.driver.get(self.create_url(params))
		if not self.fast_mode:
			self.scroll_to_bottom()
		
		raw_items = self.driver.find_elements_by_css_selector("ytd-video-renderer")

		videos = []

		for raw_item in raw_items:
			video = {"live": False}
			thumbnail = raw_item.find_element_by_css_selector("#thumbnail")
			video['url'] = thumbnail.get_attribute("href")

			# TODO: grab title
			# title = raw_item.find_elements_by_css_selector("#video-title")

			# Check if live
			elements = raw_item.find_elements_by_css_selector('[class="style-scope ytd-badge-supported-renderer"]')
			for element in elements:
				if "LIVE" in element.get_attribute('innerHTML') or "PREMIERING" in element.get_attribute('innerHTML'):
					video['live'] = True
					# If is live and no views, views don't show up, default to 0
					video['views'] = 0

			## Views
			meta_blocks = raw_item.find_elements_by_css_selector("span.style-scope.ytd-video-meta-block")
			for block in meta_blocks:
				inner_html = block.get_attribute('innerHTML')
				if "view" in inner_html or "watching" in inner_html:
					video["views"] = self.parse_views_html(inner_html)
				if "Scheduled for" in inner_html:
					video["views"] = 0

			videos.append(video)
			if self.fast_mode:
				break

		if len(videos) == 0:
			raise DangError(get_error_text(guild.id, "no_videos"))
		
		return videos

	def quit(self):
		self.driver.close()

	@commands.command(aliases=['obscure', 'obscuur'], pass_context=True,  description="Sends a random obscure video. Param is search query (optional).")
	async def s_latest(self, ctx, *params):
		async with ctx.typing():
			start_time = time()
			search_params = self.param_last_hour
			search_params['search_query'] = ' '.join(params) if len(list (params)) > 0  else ''.join(choice(string.ascii_lowercase) for i in range(3))

			items = self.get_videos(search_params, ctx.guild)

			low_views = []
			if not self.fast_mode:
				CUT_OFF_POINT = 100
				low_views = list(filter(lambda x: (x['views'] <= CUT_OFF_POINT), items))  
			
			logging.info("Youtube_s took %s seconds" % (time() - start_time))

			await ctx.send(choice(low_views)["url"] if len(low_views) > 0 else choice(items)['url'])		
