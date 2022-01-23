import datetime, os, json, logging
from random import randrange

debug_bool = True

def random_datetime_in_range(start, end):
    n_days = (end - start).days
    random_date = start + datetime.timedelta(days=randrange(n_days))
    return random_date

def get_text(guild_id, *keys):
	texts = get_config(guild_id, "texts", keys[0])
	if not texts:
		texts = get_config("default", "texts", keys[0])

	try:
		for i in range(1, len(keys)):
			texts = texts[keys[i]]
	except:
		texts = ""

	return texts

def get_error_text(guild_id, name):
	text = get_config(guild_id, "error_texts", name)
	if not text:
		text = get_config("default", "error_texts", name)
	return text

def get_config(guild_id, *keys):
	env_key = "config_" + (str(guild_id) if guild_id else "default")
	try:
		config = json.loads(os.getenv(env_key))
	except:
		config = __get_default_config()

	if not keys[0] in config:
		config = __get_default_config()
		if not keys[0] in config:
			logging.error(f"get_config: config not found for {guild_id}: {keys}")
			return ""

	try:
		for key in keys:
			config = config[key]
	except:
		logging.error(f"get_config: config not found for guild {guild_id}: {keys}")
		config = ""
	return config

def config_files_to_env():
	for file in os.listdir("config"):
		with open("config/"+file) as f:
			data = json.load(f)
			os.environ["config_" + file.rstrip(".json")] = json.dumps(data)

def __get_default_config():
	json_data = os.getenv("config_default")
	return json.loads(json_data) if json_data else {}