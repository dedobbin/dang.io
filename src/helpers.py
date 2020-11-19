import datetime, os, json
from random import randrange
from dotenv import load_dotenv

dot_env_loaded = False
texts = None
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

def get_text(*args):
    global texts
    if not texts:
        with open(env('TEXTS_FILE')) as f:
            texts = json.load(f)
    
    if len(args) == 0:
        raise (ValueError("get_text called without params"))
    
    result = ""
    try:
        result = texts[args[0]]
        
        for i in range(1, len(args)):
            result = result[args[i]]
    except KeyError as e:
        print("text not found, keys: " + str(args))
        return ""

    return result

