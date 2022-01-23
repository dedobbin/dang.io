import datetime, os, json, logging
from random import randrange

def random_datetime_in_range(start, end):
    n_days = (end - start).days
    random_date = start + datetime.timedelta(days=randrange(n_days))
    return random_date

def get_text(guild_id, *keys):
	keys = ("texts",) + keys
	texts = get_config(guild_id, *keys)
	return texts

def get_error_text(guild_id, *keys):
	keys = ("error_texts",) + keys
	texts = get_config(guild_id, *keys)
	return texts

def get_config(guild_id, *keys):
	env_key = "config_" + (str(guild_id) if guild_id else "default")
	try:
		config = json.loads(os.getenv(env_key))
	except:
		config = __get_default_config()

	try:
		for key in keys:
			config = config[key]
	except KeyError:
		if guild_id != "default":
			# Use default config as fallback
			return get_config("default", *keys)
		else:
			logging.error(f"get_config: config not found for guild {guild_id}: {keys}")
			return ""
	
	return config

def config_files_to_env():
	for file in os.listdir("config"):
		with open("config/"+file) as f:
			data = json.load(f)
			os.environ["config_" + file.rstrip(".json")] = json.dumps(data)

def __get_default_config():
	json_data = os.getenv("config_default")
	return json.loads(json_data) if json_data else {}