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
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import re
import unicodedata
import logging

# ---------------- LOGGING ----------------
log = logging.getLogger("ragebait")
log.setLevel(logging.INFO)

# ---------------- PATHS ----------------
BASE_DIR = Path(__file__).parent.parent
DB_DIR = BASE_DIR / "database"
ASSETS = BASE_DIR / "assets"
DB_PATH = DB_DIR / "ragebait.db"
OUTPUT_PATH = BASE_DIR / "ragebait_leaderboard.png"

# ---------------- IMAGE CONFIG ----------------
WIDTH, HEIGHT = 1280, 720
MAX_ENTRIES = 5

# ---------------- COLORS ----------------
TEXT_MAIN   = (255, 255, 255)
TEXT_SHADOW = (0, 0, 0)

# ---------------- RAGE WORD SETS ----------------
RAGE_SINGLE_WORDS = {
    "ratio", "cope", "seethe", "trash", "mid", "ez", "npc",
    "brainrot", "clown", "delusional", "pathetic",
    "washed", "irrelevant", "dogwater", "hardstuck",
    "boosted", "fraud", "carried", "weak", "soft",
    "boring", "cringe", "yikes"
}

RAGE_PHRASES = {
    "skill issue", "get good", "low iq", "rent free",
    "stay mad", "touch grass", "who asked",
    "nobody cares", "try harder", "cope harder",
    "common l", "aint reading all that",
}

# ---------------- HELPERS ----------------
def sanitize_username(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = re.sub(r"[^\w\s.-]", "", name)
    return (name.strip() or "User")[:20]

def normalize_content(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()

def contains_ragebait(content: str) -> bool:
    normalized = normalize_content(content)
    words = set(normalized.split())

    if words & RAGE_SINGLE_WORDS:
        return True

    for phrase in RAGE_PHRASES:
        if phrase in normalized:
            return True

    return False

# ---------------- GRADIENT PANEL ----------------
def draw_red_gradient_panel(img: Image.Image, width: int):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    for x in range(width):
        alpha = int(210 - (x / width) * 90)
        d.line([(x, 0), (x, HEIGHT)], fill=(120, 0, 0, alpha))

    return Image.alpha_composite(img, overlay)

# ---------------- COG ----------------
class Ragebait(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        DB_DIR.mkdir(exist_ok=True)

        try:
            self.font_title = ImageFont.truetype(ASSETS / "font_bold.ttf", 46)
            self.font_row = ImageFont.truetype(ASSETS / "font_regular.ttf", 30)
            self.font_small = ImageFont.truetype(ASSETS / "font_regular.ttf", 18)
        except OSError:
            self.font_title = ImageFont.load_default()
            self.font_row = ImageFont.load_default()
            self.font_small = ImageFont.load_default()

        bot.loop.create_task(self._init_db())

    async def _init_db(self):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ragebait (
                    guild_id INTEGER,
                    user_id INTEGER,
                    rage_count INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            await db.commit()

    # ---------------- MESSAGE LISTENER ----------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if not contains_ragebait(message.content):
            return

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO ragebait (guild_id, user_id, rage_count)
                VALUES (?, ?, 1)
                ON CONFLICT(guild_id, user_id)
                DO UPDATE SET rage_count = rage_count + 1
            """, (message.guild.id, message.author.id))
            await db.commit()

    # ---------------- COMMAND ----------------
    @commands.command(name="ragebait", aliases=["rb"])
    async def ragebait(self, ctx: commands.Context):
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("""
                SELECT user_id, rage_count
                FROM ragebait
                WHERE guild_id = ?
                ORDER BY rage_count DESC
                LIMIT ?
            """, (ctx.guild.id, MAX_ENTRIES))
            rows = await cursor.fetchall()

        if not rows:
            return await ctx.send("No ragebait detected yet.")

        # ---- IMAGE ----
        try:
            img = Image.open(ASSETS / "ragebait_bg.png").convert("RGBA")
        except FileNotFoundError:
            img = Image.new("RGBA", (WIDTH, HEIGHT), (30, 0, 0))

        PANEL_WIDTH = 900
        img = draw_red_gradient_panel(img, PANEL_WIDTH)
        draw = ImageDraw.Draw(img)

        CENTER_X = PANEL_WIDTH // 2

        # ---- TITLE ----
        draw.text(
            (CENTER_X, 55),
            "TOP 5 RAGEBAITED MOFOS",
            anchor="mm",
            font=self.font_title,
            fill=TEXT_MAIN,
            stroke_width=2,
            stroke_fill=TEXT_SHADOW
        )

        # ---- SUBTITLE ----
        draw.text(
            (CENTER_X, 105),
            "Users who could not keep calm",
            anchor="mm",
            font=self.font_small,
            fill=TEXT_MAIN
        )

        # ---- LIST ----
        start_y = 170
        row_h = 56

        for idx, (user_id, count) in enumerate(rows, start=1):
            member = ctx.guild.get_member(user_id)
            if not member:
                try:
                    member = await ctx.guild.fetch_member(user_id)
                except discord.NotFound:
                    member = None

            name = sanitize_username(member.name if member else f"user{user_id}")
            y = start_y + (idx - 1) * row_h

            draw.text(
                (CENTER_X, y),
                f"{idx}. {name} — {count}",
                anchor="mm",
                font=self.font_row,
                fill=TEXT_MAIN
            )

        img.save(OUTPUT_PATH)
        await ctx.send(file=discord.File(OUTPUT_PATH))
        OUTPUT_PATH.unlink(missing_ok=True)

# ---------------- SETUP ----------------
async def setup(bot: commands.Bot):
    await bot.add_cog(Ragebait(bot))
