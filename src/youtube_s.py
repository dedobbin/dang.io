from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
# from bs4 import BeautifulSoup
# import requests
from time import sleep
from discord.ext import commands
import string, os
from helpers import debug_print, get_text
from dang_error import DangError
from random import choice

########### youtube doesn't like bots, and they increase view count, which is against TOS, so use at own risk

class Youtube_S(commands.Cog):
	param_last_hour = {"sp" : "EgQIARAB"}

	def __init__(self, bot):
		options = Options()
		if not os.getenv("DEBUG_MODE"):
			options.headless = True
		self.driver = webdriver.Firefox(options=options, executable_path = os.getenv("WEBDRIVER_PATH"))
		self.bot = bot


	def scroll_to_bottom(self):
		# pretty jank, but works usually 
		# TODO: finetune for faster responses, don't need all results
		body = self.driver.find_element_by_css_selector("body")
		for j in range(0, 3):
			for i in range (0, 10):
				body.send_keys(Keys.PAGE_DOWN)
			sleep(0.5)
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

	def get_videos(self, params):
		self.driver.get(self.create_url(params))
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

			#debug_print(video)
			videos.append(video)

		if len(videos) == 0:
			raise DangError(get_text("errors", "no_videos"))
		
		return videos

	def quit(self):
		self.driver.close()

	@commands.command(aliases=['obscure', 'obscuur'], pass_context=True)
	async def s_latest(self, ctx, *params):
		search_params = self.param_last_hour
		search_params['search_query'] = ' '.join(params) if len(list (params)) > 0  else ''.join(choice(string.ascii_lowercase) for i in range(3))

		items = self.get_videos(search_params)

		CUT_OFF_POINT = 100
		low_views = list(filter(lambda x: (x['views'] <= CUT_OFF_POINT), items))  

		await ctx.send(choice(low_views)["url"])		
