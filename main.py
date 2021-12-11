"""fishy <==<3"""
from __future__ import annotations

import random
from configparser import ConfigParser
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypedDict

import discord
from discord.ext import commands
from discord.utils import escape_markdown
from mysql.connector import Error, MySQLConnection, connect


def config(filename="config.ini", section="mysql") -> Dict[str, str]:
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f"Section {section} not found in the {filename} file")

    return db


def execute(
    command: str, data: Tuple[Any, ...] = tuple()
) -> Optional[List[Tuple[Any, ...]]]:
    result = None
    try:
        conn = MySQLConnection(**config())
        cursor = conn.cursor()
        cursor.execute(command, data)
        result = cursor.fetchall()
        conn.commit()

    except Error as e:
        if not None:
            print(f"{command=}")
        raise e

    finally:
        cursor.close()
        conn.close()

    if result is not None:
        return result
    return None


bot = commands.Bot(command_prefix="$")


def fish_common():
    return random.randint(1, 29)


def fish_uncommon():
    return random.randint(30, 99)


def fish_rare():
    return random.randint(100, 399)


def fish_legendary():
    return random.randint(400, 750)


def trash():
    return 0


WEIGHTS = [9, 60, 20, 10, 1]
FISHTYPES = {
    "trash": trash,
    "common": fish_common,
    "uncommon": fish_uncommon,
    "rare": fish_rare,
    "legendary": fish_legendary,
}
TRASH_ICONS = [
    ":moyai:",
    ":stopwatch:",
    ":wrench:",
    ":pick:",
    ":nut_and_bolt:",
    ":gear:",
    ":toilet:",
    ":alembic:",
    ":bathtub:",
    ":scissors:",
    ":boot:",
    ":high_heel:",
    ":saxophone:",
    ":trumpet:",
    ":anchor:",
    ":shopping_cart:",
    ":paperclips:",
    ":paperclip:",
    ":prayer_beads:",
    ":oil:",
    ":compression:",
    ":radio:",
    ":fax:",
    ":movie_camera:",
    ":projector:",
    ":guitar:",
    ":violin:",
    ":telephone:",
    ":alarm_clock:",
    ":fire_extinguisher:",
    ":screwdriver:",
    ":wrench:",
    ":magnet:",
    ":coffin:",
    ":urn:",
    ":amphora:",
    ":crystal_ball:",
    ":telescope:",
    ":microscope:",
    ":microbe:",
    ":broom:",
    ":basket:",
    ":sewing_needle:",
    ":roll_of_paper:",
    ":plunger:",
    ":bucket:",
    ":toothbrush:",
    ":soap:",
    ":razor:",
    ":sponge:",
    ":squeeze_bottle:",
    ":key:",
    ":teddy_bear:",
    ":frame_photo:",
    ":nesting_dolls:",
    ":izakaya_lantern:",
    ":wind_chime:",
    ":safety_pin:",
    ":newspaper2:",
]


@bot.command(aliases=["fish", "fihy", "fisy", "foshy", "fisyh", "fsihy", "fin"])
async def fishy(ctx, user=None):
    """Go fishing."""
    catch = random.choices(list(FISHTYPES.keys()), WEIGHTS)[0]
    fish = FISHTYPES[catch]()
    execute("insert into fish (amount) values (%s)", tuple([fish]))
    if fish == 0:
        await ctx.send(f"you caught trash {random.choice(TRASH_ICONS)}")
    else:
        await ctx.send(
            f"you caught {fish} {catch} fishy {(lambda x: '🐟' if x=='' else x)('🐟' * int(fish // 10))}"
        )


@bot.command()
async def globalfishstats(ctx):
    query = execute("select sum(amount) from fish")[0][0]
    if query is not None:
        await ctx.send(f"{query} digital fishy fished 🎣")


if __name__ == "__main__":
    bot.run(
        "OTE4OTk2OTI3OTgxNDI0NjQw.YbPYlQ.oKQNxw2xIHaGqoRMHWOghUootjE"
    )  # (os.environ["DISCORDFISH_TOKEN"])
