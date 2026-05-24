
# Hashbot

**Overview:** This bot provides message listeners and image-based leaderboards for in-server activity. It saves stats to local sqlite databases and renders leaderboard images using the `Pillow` library.

**Requirements:**
- Python 3.10 or newer
- `pip` and virtual environment tools
- A Discord bot token

## Contents
- `main.py` — bot entrypoint and cog loader
- `cogs/` — modular command/event cogs
	- `ragebait.py` — detects "ragebait" messages and produces a top-5 image leaderboard (`^ragebait`, `^rb`)
	- `touch_grass.py` — awards simple XP for activity and produces a top-5 image leaderboard (`^touchgrass`, `^tg`)
    - more soon <3
- `assets/` — optional fonts and background images used by the cogs
- `database/` — sqlite DB files created at runtime

## Setup (Windows)
1. Create and activate a virtual environment:

```powershell
python -m venv myenv

# HashBot

HashBot — a trendy leaderboard bot with stylish image-based leaderboards. It follows the trend.

**Overview:** HashBot listens to server activity and generates eye-catching leaderboard images (top users, XP, and other trends). It stores stats in local sqlite databases and renders visuals using `Pillow`.

**Requirements:**
- Python 3.10 or newer
- `pip` and virtual environment tools
- A Discord bot token

## Contents
- `main.py` — bot entrypoint and cog loader
- `cogs/` — modular command/event cogs
	- `ragebait.py` — detects "ragebait" messages and produces a top-5 image leaderboard (`^ragebait`, `^rb`)
	- `touch_grass.py` — awards simple XP for activity and produces a top-5 image leaderboard (`^touchgrass`, `^tg`)
- `assets/` — optional fonts and background images used by the cogs
- `database/` — sqlite DB files created at runtime

## Setup (Windows)
1. Create and activate a virtual environment:

```powershell
python -m venv myenv
myenv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create a `.env` file in the project root containing your bot token:

```text
DISCORD_TOKEN=your_bot_token_here
```

4. (Optional) Place fonts and background images in the `assets/` folder if you want custom visuals. The cogs fall back to default fonts/images if assets are missing.

## Running

Start the bot from the project root:

```powershell
python main.py
```

HashBot uses the command prefix `^` (caret). Built-in commands:
- `^ping` — basic liveness/latency check
- `^ragebait` (alias `^rb`) — generate the Ragebait leaderboard image
- `^touchgrass` (alias `^tg`) — generate the Touch Grass leaderboard image

## Data & Files
- Databases are stored in the `database/` folder as sqlite files (created automatically).
- Generated leaderboard images are created in the project root and removed after being sent by the bot.

## Notes
- `main.py` expects `DISCORD_TOKEN` to be present in the environment (it uses `python-dotenv` to load `.env`).
- If fonts or image assets are not present, the cogs use Pillow's default fonts and a solid background.

## Next steps (suggestions)
- Add a `requirements.txt` lock or `pyproject.toml` for reproducible installs.
- Add GitHub Actions to run flake8/pytest and a simple deploy workflow.
- Add more cogs or trendy leaderboard styles (themes, colors, badges).

---

Updated README to name the project `HashBot` and highlight trendy leaderboards.

## © Copyright

© 2026 Jade.  
All rights reserved.


