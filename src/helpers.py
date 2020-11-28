import datetime, os, json, re, os
from random import randrange
import os

texts = {}

debug_bool = True

def random_datetime_in_range(start, end):
    n_days = (end - start).days
    random_date = start + datetime.timedelta(days=randrange(n_days))
    return random_date

def debug_print(input):
	if os.getenv("DEBUG_MODE"):
		print("<DEBUG> " + str(input))

def get_emoji(name, guild):
	if not guild:
		debug_print("Requested emoji without guild..")
		return ""
	for emoji in guild.emojis:
		if emoji.name == name:
			return str(emoji)
	
	debug_print('couldn not find emoji ' + name)
	return ''

def get_text(*args, guild = None):
	# TODO: now reads all strings into memory, maybe shouldn't ?
	global texts

	if len(args) == 0:
		raise (ValueError("get_text called without params"))

	key = guild.id if guild else 'default' 

	try:
		guild_texts = texts[key]
	except KeyError as e:
			guild_texts = texts[key] = get_config("texts",config_folder = guild_to_config_path(guild))
			texts[key] = parse_str_emoji(texts[key], guild)
			guild_texts = texts[key]

	# When not found in guild texts, check default file..	
	if not args[0] in guild_texts:
		guild_texts[args[0]] = get_config("texts")[args[0]]

	result = ""
	
	try:
		result = guild_texts[args[0]]

		for i in range(1, len(args)):
			result = result[args[i]]
	except KeyError as e:
		print("text not found, keys: " + str(args))
		raise

	return result

# Replace ___EMOJI_EMOJINAME___ with proper emoji, based on emoji_map
def parse_str_emoji(teh_string, guild):
	if not guild:
		debug_print("Tried to parse_str_emoji without guild..")
		return teh_string
	
	# If teh_string is secretly not a string
	if isinstance(teh_string, dict):
		parsed = {};
		for key in teh_string:
			parsed[key] = parse_str_emoji(teh_string[key], guild)
		return parsed
	elif isinstance(teh_string, list):
		parsed = [];
		for r in teh_string:
			parsed.append(parse_str_emoji(r, guild))
		return parsed

	# actual string operations
	p = re.compile(r"___EMOJI_[a-zA-Z0-9_]*___")
	for res in re.findall(p, teh_string):
		emoji = res.strip("___").lstrip("EMOJI_")
		teh_string = teh_string.replace(res, get_emoji(emoji, guild))	
		
	return teh_string

#TODO: optimize, does quite some IO etc
def get_config(*keys, config_folder = "config/default", file="config.json"):
	if not os.path.isfile(config_folder + "/" + file):
		if config_folder != "config/default":
			config_folder = "config/default"
			if not os.path.isfile(config_folder + "/" + file):
				raise RuntimeError("No config file or fallback found:" + config_folder + "/" + file)

	possbile_folders = [config_folder, "config/default"] if not config_folder == "config/default" else ["config/default"]

	for folder in possbile_folders:		
		config = None
		with open(folder + "/" + file) as f:
			config = json.load(f)
		try:
			result = config[keys[0]]
			for i in range(1, len(keys)):
				result = result[keys[i]]
			return result
		except KeyError:
			continue
	
	raise RuntimeError("No config found for " + str(keys))

def guild_to_config_path(guild):
	return "config/" + str(guild.id) + "/" if guild else "config/default/"

# Test stuff
if __name__ == "__main__":
	from dotenv import load_dotenv
	load_dotenv()

	assert "guild_config" == get_config("test", config_folder = "config/" + os.getenv("TEST_GUILD_ID"))
	
	assert "default_config" == get_config("test", config_folder = "config/nonexistent")
	
	assert "default_config" == get_config("test")
	
	assert "fallback_value" == get_config("fallback_test", config_folder = "config/" + os.getenv("TEST_GUILD_ID"))
	
	try:
		get_config("nonexistent", config_folder = "config/" + os.getenv("TEST_GUILD_ID"))
	except RuntimeError as e:
		assert "No config found for" in str(e)

	get_config_return_value = None
	try:
		get_config_return_value = get_config("nonexistent", config_folder = "config/nonexistent")
	except RuntimeError as e:
		assert "No config found for" in str(e)
	assert get_config_return_value == None

	get_config_return_value = None
	try:
		get_config_return_value = get_config("nonexistent")
	except RuntimeError as e:
		assert "No config found for" in str(e)
	assert get_config_return_value == None

