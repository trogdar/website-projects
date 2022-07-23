"""Main entry point for running both server and bot."""

import web_server
import discord_bot

from constants import RUN_LOCAL,BOT_TOKEN


flask_options = {}

if not RUN_LOCAL:
    flask_options = {'host': '0.0.0.0'}

#discord_bot.main()

wp=web_server.WebProcess(target=web_server.WebProcess.run,kwargs=flask_options)
wp.start()  