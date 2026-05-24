""" Copyright © 2026 ElseIfVoid

All rights reserved.

This software and its source code are provided for personal and educational use.
Redistribution, modification, or commercial use of this software, in whole or
in part, without explicit permission from the author is prohibited.

You may run and modify this software for private use.
You may not resell, rebrand, or redistribute it as your own work. """

import discord
from discord.ext import commands
import aiosqlite
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import re
import unicodedata
import logging

log = logging.getLogger("touch_grass")
log.setLevel(logging.INFO)

BASE_DIR = Path(__file__).parent.parent
DB_DIR = BASE_DIR / "database"
ASSETS = BASE_DIR / "assets"
DB_PATH = DB_DIR / "touch_grass.db"
OUTPUT_PATH = BASE_DIR / "touch_grass_leaderboard.png"

WIDTH, HEIGHT = 736, 414
XP_COOLDOWN = 60
XP_PER_TICK = 5
MAX_ENTRIES = 5

TEXT_WHITE = (255, 255, 255)
TEXT_SHADOW = (0, 0, 0)

def sanitize_username(name: str) -> str:
    try:
        name = unicodedata.normalize("NFKD", name)
        name = name.encode("ascii", "ignore").decode("ascii")
        name = re.sub(r"[^\w\s.-]", "", name)
        return (name.strip() or "User")[:17]
    except Exception:
        log.exception("Failed to sanitize username")
        return "User"

def apply_green_gradient(img: Image.Image) -> Image.Image:
    gradient = Image.new("RGBA", img.size, color=0)
    draw = ImageDraw.Draw(gradient)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(20 + (40 - 20) * ratio)
        g = int(120 + (200 - 120) * ratio)
        b = int(20 + (40 - 20) * ratio)
        draw.line((0, y, WIDTH, y), fill=(r, g, b, 140))

    return Image.alpha_composite(img, gradient)

class TouchGrass(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        DB_DIR.mkdir(exist_ok=True)

        try:
            self.font_title = ImageFont.truetype(ASSETS / "font_bold.ttf", 42)
            self.font_row = ImageFont.truetype(ASSETS / "font_regular.ttf", 28)
            self.font_small = ImageFont.truetype(ASSETS / "font_regular.ttf", 18)
        except OSError:
            log.warning("Fonts not found, using default fonts")
            self.font_title = ImageFont.load_default()
            self.font_row = ImageFont.load_default()
            self.font_small = ImageFont.load_default()

        bot.loop.create_task(self._init_db())

    async def _init_db(self):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS touch_grass (
                    guild_id INTEGER,
                    user_id INTEGER,
                    xp INTEGER DEFAULT 0,
                    last_message INTEGER,
                    PRIMARY KEY (guild_id, user_id)
                )
                """
            )
            await db.commit()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (
            message.author.bot
            or not message.guild
            or message.content.startswith(tuple(self.bot.command_prefix))
        ):
            return

        now = int(time.time())

        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                "SELECT last_message FROM touch_grass WHERE guild_id = ? AND user_id = ?",
                (message.guild.id, message.author.id),
            )
            row = await cursor.fetchone()
            await cursor.close()

            if row and row[0] and now - row[0] < XP_COOLDOWN:
                return

            if row:
                await db.execute(
                    "UPDATE touch_grass SET xp = xp + ?, last_message = ? WHERE guild_id = ? AND user_id = ?",
                    (XP_PER_TICK, now, message.guild.id, message.author.id),
                )
            else:
                await db.execute(
                    "INSERT INTO touch_grass (guild_id, user_id, xp, last_message) VALUES (?, ?, ?, ?)",
                    (message.guild.id, message.author.id, XP_PER_TICK, now),
                )

            await db.commit()

    @commands.command(
        name="touchgrass",
        aliases=["tg"],
        help="Shows the Touch Grass leaderboard (time-based XP, image output)."
    )
    async def touch_grass(self, ctx: commands.Context):
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                """
                SELECT user_id, xp
                FROM touch_grass
                WHERE guild_id = ?
                ORDER BY xp DESC
                LIMIT ?
                """,
                (ctx.guild.id, MAX_ENTRIES),
            )
            rows = await cursor.fetchall()
            await cursor.close()

        if not rows:
            return await ctx.send("No data yet.")

        try:
            img = Image.open(ASSETS / "grass_bg.png").convert("RGBA")
        except FileNotFoundError:
            img = Image.new("RGBA", (WIDTH, HEIGHT), (30, 120, 30))

        img = apply_green_gradient(img)
        draw = ImageDraw.Draw(img)

        draw.text(
            (WIDTH // 2, 36),
            "TOUCH GRASS MOFOS",
            anchor="mm",
            font=self.font_title,
            fill=TEXT_WHITE,
        )

        draw.text(
            (WIDTH // 2, 68),
            "Top 5 unemployed XP leaderboard",
            anchor="mm",
            font=self.font_small,
            fill=TEXT_WHITE,
        )

        start_y = 120
        row_h = 44

        for idx, (user_id, xp) in enumerate(rows, start=1):
            member = ctx.guild.get_member(user_id)
            if not member:
                try:
                    member = await ctx.guild.fetch_member(user_id)
                except discord.NotFound:
                    member = None

            raw_name = member.name if member else f"user{user_id}"
            name = sanitize_username(raw_name)
            y = start_y + (idx - 1) * row_h

            draw.text((80, y + 2), f"{idx}. {name} - {xp} XP", font=self.font_row, fill=TEXT_SHADOW)
            draw.text((80, y), f"{idx}. {name} - {xp} XP", font=self.font_row, fill=TEXT_WHITE)

        img.save(OUTPUT_PATH)
        await ctx.send(file=discord.File(OUTPUT_PATH))

        if OUTPUT_PATH.exists():
            OUTPUT_PATH.unlink()

async def setup(bot: commands.Bot):
    await bot.add_cog(TouchGrass(bot))
