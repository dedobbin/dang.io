import datetime, os, json, re, os
from random import randrange
import os


debug_bool = True

def random_datetime_in_range(start, end):
    n_days = (end - start).days
    random_date = start + datetime.timedelta(days=randrange(n_days))
    return random_date

def debug_print(input):
	if os.getenv("DEBUG_MODE"):
		print("<DEBUG> " + str(input))

def get_texts(guild_id, *keys):
	texts = get_config(guild_id, "texts", keys[0])
	if not texts:
		texts = get_config("default", "texts", keys[0])

	try:
		for i in range(1, len(keys)):
			texts = texts[keys[i]]
	except:
		texts = ""

	return texts


def get_config(guild_id, *keys):
	env_key = "config_" + (guild_id if guild_id else "default")
	try:
		config = json.loads(os.getenv(env_key))
	except:
		config =  json.loads(os.getenv("config_default"))

	if not keys[0] in config:
		config = json.loads(os.getenv("config_default"))
		if not keys[0] in config:
			print("unknown config")
			return ""

	try:
		for key in keys:
			config = config[key]
	except:
		config = ""
	return config

def guild_to_config_path(guild):
	return ""

def config_files_to_env():
	for file in os.listdir("config"):
		with open("config/"+file) as f:
			data = json.load(f)
			os.environ["config_" + file.rstrip(".json")] = json.dumps(data)
			# debug_print("Set env: " + "config_" + file.rstrip(".json"))

# Test stuff
if __name__ == "__main__":
	from dotenv import load_dotenv
	load_dotenv()

	config_files_to_env()
	
	assert "" == get_config( os.getenv("TEST_GUILD_ID"), "nonexistant")

	assert "" == get_config(None, "nonexistant")

	assert "guild_config" == get_config(os.getenv("TEST_GUILD_ID"),"test")

	data = get_config(os.getenv("TEST_GUILD_ID"),"nested_test", "layer_one")
	assert (data["layer_two"] == "core")
	
	assert "core" == get_config(os.getenv("TEST_GUILD_ID"),"nested_test", "layer_one", "layer_two")

	assert "" == get_config(os.getenv("TEST_GUILD_ID"),"nested_test", "layer_one", "layer_two", "nonexistant")

	assert "default_config" == get_config(None, "test")

	assert "default_config" == get_config("nonexistant", "test")

	assert "fallback_value" == get_config(os.getenv("TEST_GUILD_ID"), "fallback_test")
	
	assert "niks" in get_texts(os.getenv("TEST_GUILD_ID"), "errors", "no_videos")

	assert "this is some text" == get_texts(os.getenv("TEST_GUILD_ID"), "some_text")

	assert "nothing found" == get_texts("nonexistant", "errors", "no_videos")


