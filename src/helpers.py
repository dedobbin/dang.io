import datetime, os, json, re
from random import randrange
import os

texts = {}

debug_bool = True

def config_file_path(file, guild = None):
    default_file_path = 'config/default/' + file
    specific_file_path = 'config/' + str(guild.id) + '/' + file if guild else None

    if guild and os.path.isfile(specific_file_path):
        return specific_file_path
    
    if guild and os.path.isfile(default_file_path):
        print('No specific ' + file + ' config found for ' + guild.name + ', using default')
        return default_file_path

    raise RuntimeError('Config file ' + file + ' not found')


def random_datetime_in_range(start, end):
    n_days = (end - start).days
    random_date = start + datetime.timedelta(days=randrange(n_days))
    return random_date

def debug_print(input):
	if debug_bool:
		if (isinstance(input, str)):
			print("<DEBUG> " + input)
		else:
			print("<DEBUG> ")
			print(input)


def get_emoji(name, guild):
	if not guild:
		debug_print("Requested emoji without guild..")
		return ""
	for emoji in guild.emojis:
		if emoji.name == name:
			return str(emoji)
	
	debug_print('couldn not find emoji ' + name)
	return ''

# If you expect array/dict back with alot of entries, while you want to pick only one, you can bypass emoji_parse stage 
def get_text(*args, guild = None):
	global texts
	try:
		guild_texts = texts[guild.id ]
	except KeyError as e:
		with open(config_file_path('texts.json', guild)) as f:
			texts[guild.id ] = json.load(f)
			guild_texts = texts[guild.id ]

	if len(args) == 0:
		raise (ValueError("get_text called without params"))

	result = ""
	try:
		result = guild_texts[args[0]]

		for i in range(1, len(args)):
			result = result[args[i]]
	except KeyError as e:
		print("text not found, keys: " + str(args))
		return ""

    #TODO: cache
	return parse_str_emoji(result, guild)

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