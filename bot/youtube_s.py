import os
import logging
import string
from random import choice
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
# from bs4 import BeautifulSoup
from selenium import webdriver

########### youtube doesn't like bots, and they increase view count, which is against TOS, so use at own risk

class Youtube_S:
    param_last_hour = {"sp" : "EgQIARAB"}  #TODO: make it possible to obtain these obfuscated params, even though they haven't changed in a year..
    
    def __init__(self, fast_mode = False):
        self.fast_mode = fast_mode
        option = webdriver.ChromeOptions()
        if not os.getenv("DEBUG_MODE"):
            option.add_argument("--headless")
            option.add_argument('--disable-gpu')
        try:
            self.driver = self.create_web_driver(option)
        except Exception as e:
            logging.error("couldn't start web driver:" +  str(e))
            raise e
    
    def get_obscure_videos(self, *params):
        search_params = self.param_last_hour
        search_params['search_query'] = ' '.join(params) if len(list (params)) > 0  else ''.join(choice(string.ascii_lowercase) for i in range(3))
        items = self.get_videos(search_params)
        if not self.fast_mode:
            CUT_OFF_POINT = 100
            items = list(filter(lambda x: (x['views'] <= CUT_OFF_POINT), items))  
        
        return items

    #TODO: example how to call with search params like in get_obscure_videos
    def get_videos(self, params):
        self.driver.get(self.__create_url(params))
        if not self.fast_mode:
            self.__scroll_to_bottom()
        
        raw_items = self.driver.find_elements_by_css_selector("ytd-video-renderer")

        videos = []

        for raw_item in raw_items:
            #TODO: it seems there is a case where views are not correctly scraped
            video = {"live": False, "views": 0}
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
                    video["views"] = self.__parse_views_html(inner_html)
                if "Scheduled for" in inner_html:
                    video["views"] = 0

            videos.append(video)
            if self.fast_mode:
                break

        return videos

    def quit(self):
        self.driver.close()

    def sanity_check(self):
        return not not self.driver

    def create_web_driver(self, options):
        args = {'options': options}
        path = os.getenv('CHROME_EXECUTABLE_PATH')
        if path:
            args['executable_path'] = path
        return webdriver.Chrome(**args)

    def __scroll_to_bottom(self):
        # pretty jank, but works usually 
        # TODO: finetune for faster responses, don't need all results
        body = self.driver.find_element_by_css_selector("body")
        for i in range (0, 100):
            body.send_keys(Keys.PAGE_DOWN)
        return

    def __create_url(self, params):
        url = "https://www.youtube.com/results"

        if len(params) > 0:
            url += "?"
            for key in params:
                url+= key + "=" + params[key] + "&"
            url =  url.rstrip("&")
        
        return url

    def __parse_views_html(self, inner_html):
        if "K" in inner_html:
            # uh..
            res = (inner_html.replace("K", "000") if not "." in inner_html else inner_html.replace(".", "") + "00").replace("K", "").replace(" ", "")
        else:
            res = inner_html.replace("No", "0")

        res = int(''.join(filter(str.isdigit, res)))

        return res