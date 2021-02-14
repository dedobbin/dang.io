#########################################
######### Shoutouts to Dang Do #########
#########################################

import os, json, sys, string, csv, datetime
from dotenv import load_dotenv
from random import choice, randrange
import discord as discord_api
from discord.ext import commands
import inspect
from youtube import Youtube, YoutubeChannel
from youtube_s import Youtube_S
from dang_error import DangError
from helpers import get_text, get_error_text, get_config, config_files_to_env
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

load_dotenv()
config_files_to_env()


DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=['dang! ', '!dang ', 'dang!'], help_command=None)
bot.add_cog(Youtube(bot))
bot.add_cog(Youtube_S(bot))

def get_random_quote(guild):
	return choice(get_text(guild.id, "quotes"))

def magic_eight_ball(guild):
	return choice(get_text(guild.id, "magic_eight_ball"))

def should_send_random_message(guild = None):
	freq = get_config(guild.id, "spam_freq")
	if (freq <= 0):
		return False
	c = randrange(0, freq )
	return c == 0

@bot.command(name='mooi',  description="An inspirational quote.")
async def send_quote(ctx):
	await ctx.send(get_random_quote(ctx.guild))

@bot.command(name="help", description="Shows this message.")
async def help(ctx):
	has_default_channel = bool(bot.get_cog("Youtube").get_default_channel(ctx.guild))
	
	embed=discord_api.Embed()

	for command in bot.commands:
		if command.name == "latest" and not has_default_channel:
			#Latest can only be used when default channel is set
			continue 
		name = "|".join(command.aliases) if len(command.aliases) else command.name
		description = f"{command.description}"
		if "random" in command.aliases and not has_default_channel:
			#Default param only works when default channel is set, bit hacky..
			description = '.'.join(filter(lambda x: "use param 'default'" not in x, description.split(".")))
		description+= "\n"

		embed.add_field(name=name, value=description, inline=False)
	
	await ctx.send(embed=embed)

# TODO: also handle errors in events
@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandInvokeError) and isinstance(error.original, DangError):
		#logging.error("Dang error: " + str(error))
		await ctx.send(str(error.original))
	elif isinstance(error, commands.CommandNotFound):
		logging.error(str(error) + " (" + ctx.guild.name + ")")
		await ctx.send(get_error_text(ctx.guild.id, "unknown_command"))
	else:
		await ctx.send(get_error_text(ctx.guild.id, "general"))
		raise error

@bot.event
async def on_ready():
	print('Went online in')
	for g in bot.guilds:
		print(g.name + '(' + str(g.id) + ')')

@bot.event
async def on_message(message):
	if(message.author.bot):
		# if 'www.youtube.com' in message.content:
		# 	logging.info('sent video')
		return

	#logger.info("message received, " + str(message.author) + ": " + message.content)

	if ('<@!%s>' % bot.user.id) in message.content or ('<@%s>' % bot.user.id) in message.content:
		await message.channel.send(magic_eight_ball(message.guild))

	elif should_send_random_message(message.guild):
		await message.channel.send(get_random_quote(message.guild))

	await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
