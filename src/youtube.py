import sys, os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from helpers import debug_print, env
from dang_error import DangError

youtube_api = None

def youtube_auth(oauth = False):
	global youtube_api
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
		youtube_api = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
	else:
		youtube_api = googleapiclient.discovery.build(api_service_name, api_version, developerKey=YOUTUBE_API_KEY)

def search(dynamic_params, all_pages = False):
	if youtube_api == None:
		youtube_auth()

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
		raise DangError("ik heb geen verbinding met youtube <:cry:770284714481025087>")
	
	if all_pages and num_expected != len(items):
		debug_print("Only got " + str(len(items)) + " of " + str(num_expected) + "videos?")

	if len(items) == 0:
		raise DangError("ik kan geen videos vinden <:cry:770284714481025087>")

	return items