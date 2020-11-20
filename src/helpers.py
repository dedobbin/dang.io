import datetime, os, json
from random import randrange
import os

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

