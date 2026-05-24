""" Copyright © 2026 ElseIfVoid

All rights reserved.

This software and its source code are provided for personal and educational use.
Redistribution, modification, or commercial use of this software, in whole or
in part, without explicit permission from the author is prohibited.

You may run and modify this software for private use.
You may not resell, rebrand, or redistribute it as your own work. """


import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path
import logging

# -----------------------------
# ENV & LOGGING
# -----------------------------
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not found in .env file")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# -----------------------------
# INTENTS
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True

# -----------------------------
# BOT INIT
# -----------------------------
bot = commands.Bot(
    command_prefix="^",
    intents=intents,
    help_command=None,
    case_insensitive=True,  # small UX win
)

# -----------------------------
# COG LOADING
# -----------------------------
@bot.event
async def setup_hook():
    cogs_path = Path("cogs")

    for cog in cogs_path.glob("*.py"):
        if cog.name.startswith("_"):
            continue

        extension = f"cogs.{cog.stem}"

        try:
            await bot.load_extension(extension)
            logging.info(f"Loaded cog: {extension}")
        except Exception as e:
            logging.exception(f"Failed to load cog: {extension}")

# -----------------------------
# EVENTS
# -----------------------------
@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        return

    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return  # silent ignore

    # log real errors cleanly
    logging.exception(
        "Command error",
        extra={
            "guild": ctx.guild.id if ctx.guild else None,
            "user": ctx.author.id,
            "command": ctx.command,
        },
    )

# -----------------------------
# COMMANDS
# -----------------------------
@bot.command()
async def ping(ctx: commands.Context):
    await ctx.send(
        f"`❤️ Pong! {round(bot.latency * 1000)}ms`\n"
        "**Bot is alive and kicking sir !!!**"
    )

# -----------------------------
# RUN
# -----------------------------
bot.run(TOKEN)
