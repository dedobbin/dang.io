import datetime, os, json
from random import randrange
from dotenv import load_dotenv

dot_env_loaded = False
env_path = None
debug_bool = True

def random_datetime_in_range(start, end):
    n_days = (end - start).days
    random_date = start + datetime.timedelta(days=randrange(n_days))
    return random_date

def set_env_path(path):
    global env_path
    env_path = path

def env(key):
    global dot_env_loaded, env_path
    if not dot_env_loaded:
        load_dotenv(dotenv_path=env_path)
        dot_env_loaded = True
    
    return os.getenv(key)

def debug_print(input):
	if debug_bool:
		if (isinstance(input, str)):
			print("<DEBUG> " + input)
		else:
			print("<DEBUG> ")
			print(input)

