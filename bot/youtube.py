import os, logging, datetime
from random import randrange
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import config
from dang_error import DangError

class Youtube:
    def __init__(self):
        self.youtube_api = None
        try:
            self.youtube_auth()
        except Exception as e:
            logging.error(f'Failed to connect to Youtube: {e}')

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
            raise DangError(config.get_error_text(guild.id, 'youtube'))

        if all_pages and num_expected != len(items):
            logging.warning("Only got " + str(len(items)) + " of " + str(num_expected) + "videos?")

        #self.search_results.append({'result': response, 'params': params})

        if len(items) == 0:
            raise DangError(config.get_error_text(guild.id, 'no_videos'))

        return SearchResult(response, params)

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