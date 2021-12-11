"""fishy <==<3"""

from __future__ import annotations

import os
import random
from configparser import ConfigParser
from datetime import datetime, timedelta
from functools import wraps
from textwrap import dedent
from typing import Any, Callable, Dict, List, Optional, Tuple, TypedDict, Union

import discord
from discord import user
from discord.ext import commands
from discord.utils import escape_markdown
from mysql.connector import Error, MySQLConnection, connect
from prettytable import PrettyTable


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

    return result


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="$", intents=intents)


def trash():
    return 0


def fish_common():
    return random.randint(1, 29)


def fish_uncommon():
    return random.randint(30, 99)


def fish_rare():
    return random.randint(100, 399)


def fish_legendary():
    return random.randint(400, 750)


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

ALLOWED_FISH_TIME_DELTA = timedelta(seconds=10)


@bot.command(aliases=["fosh", "fish", "fihy", "fisy", "foshy", "fisyh", "fsihy", "fin"])
async def fishy(ctx, user=None):
    """Go fishing."""

    # --- can we fish? ---
    last_fish_time = execute(
        """
        SELECT MAX(fish_time)
        FROM fish
        WHERE fisher_id = %s""",
        tuple([ctx.message.author.id]),
    )[0][0]
    fish_time = datetime.now()
    if last_fish_time is not None:
        # print(f"{last_fish_time=}", f"{fish_time=}")
        # print(fish_time - last_fish_time)
        if (fish_time - last_fish_time) < ALLOWED_FISH_TIME_DELTA:
            await ctx.send(
                f"too fast cowboy 🏃 can fish in {(ALLOWED_FISH_TIME_DELTA - (fish_time - last_fish_time)).seconds} seconds 🎣"
            )
            return

    # --- we can fish! ---
    fish_time = fish_time.strftime("%Y-%m-%d %H:%M:%S")
    catch = random.choices(list(FISHTYPES.keys()), WEIGHTS)[0]
    fish_amount = FISHTYPES[catch]()
    execute(
        """
        INSERT INTO fish (fisher_id, fish_time, fish_amount)
        VALUES (%s, %s, %s)""",
        tuple([ctx.message.author.id, fish_time, fish_amount]),
    )
    # print(ctx.message.author.id)
    # print(ctx.message.author.name, "#", ctx.message.author.discriminator)
    # print(ctx.message.guild.id, ctx.message.guild.name)
    execute(
        """
        INSERT INTO users (user_id, name, discriminator)
        VALUES (%(user_id)s, %(name)s, %(discriminator)s)
        ON DUPLICATE KEY UPDATE
            name = %(name)s,
            discriminator = %(discriminator)s
        """,
        {
            "user_id": ctx.message.author.id,
            "name": ctx.message.author.name,
            "discriminator": ctx.message.author.discriminator,
        },
    )

    if fish_amount == 0:
        await ctx.send(f"(you) caught trash {random.choice(TRASH_ICONS)}")
    else:
        await ctx.send(
            f"(you) caught {fish_amount} {catch} fishy {(lambda x: '🐟' if x=='' else x)('🐟' * int(fish_amount // 10))}"
        )


@bot.command()
async def globalfishstats(ctx):
    query_global_count = execute(
        "select sum(fish_amount) from fish f inner join users u on f.fisher_id = u.user_id"
    )[0][0]
    query_fish_type_count = execute(
        """
    select concat_ws('#', u.name, u.discriminator) `fisher`
        , sum(fish_amount) `fishies`
        , count(case when fish_amount = 0 then 'trash' else null end) `trash`
        , count(case when fish_amount >= 1 and fish_amount <= 29 then 'common' else null end) `common`
        , count(case when fish_amount >= 30 and fish_amount <= 99 then 'uncommon' else null end) `uncommon`
        , count(case when fish_amount >= 100 and fish_amount <= 399 then 'rare' else null end) `rare`
        , count(case when fish_amount >= 400 and fish_amount <= 750 then 'legendary' else null end) `legendary`
    from fish f
        inner join users u
            on f.fisher_id = u.user_id
    -- where u.user_id = %(user_id)s
    group by fisher_id
    order by sum(fish_amount) desc, u.name, u.discriminator""",
        {"user_id": ctx.message.author.id},
    )
    table = PrettyTable()
    table.field_names = [
        "fisher",
        "fishies",
        "trash",
        "common",
        "uncommon",
        "rare",
        "legendary",
    ]
    table.add_rows(query_fish_type_count)
    if query_fish_type_count is not None and query_global_count is not None:
        await ctx.send(
            f"{query_global_count} digital fishy fished 🎣" "```\n" + str(table) + "```"
        )


@bot.command(
    aliases=[
        "fihystats",
        "fisystats",
        "foshystats",
        "fisyhstats",
        "fsihystats",
        "finstats",
    ]
)
async def fishstats(ctx):
    query_fish_sum = execute(
        "select sum(fish_amount) from fish where fisher_id = %s",
        tuple([ctx.message.author.id]),
    )[0][0]
    query_fish_type_count = execute(
        """
    select concat_ws('#', u.name, u.discriminator) `fisher`
        , sum(fish_amount) `fishies`
        , count(case when fish_amount = 0 then 'trash' else null end) `trash`
        , count(case when fish_amount >= 1 and fish_amount <= 29 then 'common' else null end) `common`
        , count(case when fish_amount >= 30 and fish_amount <= 99 then 'uncommon' else null end) `uncommon`
        , count(case when fish_amount >= 100 and fish_amount <= 399 then 'rare' else null end) `rare`
        , count(case when fish_amount >= 400 and fish_amount <= 750 then 'legendary' else null end) `legendary`
    from fish f
        inner join users u
            on f.fisher_id = u.user_id
    where u.user_id = %(user_id)s
    group by fisher_id
    -- order by sum(fish_amount) desc, u.name, u.discriminator""",
        {"user_id": ctx.message.author.id},
    )
    table = PrettyTable()
    table.field_names = [
        "fisher",
        "fishies",
        "trash",
        "common",
        "uncommon",
        "rare",
        "legendary",
    ]
    table.add_rows(query_fish_type_count)
    if query_fish_sum is not None and query_fish_type_count is not None:
        await ctx.send(
            f"(you)'ve fished {query_fish_sum} digital fishy 🎣\n"
            "```\n" + str(table) + "```"
        )


@bot.command()
async def getuser(ctx, *, user: discord.Member = None, id: int = None):
    if user is not None:
        user_name = bot.get_user(user.id)  # (int(id))
        print(f"{user_name=}")


@bot.command()
async def fishyboard(ctx):
    cmd = """
    select rank() over(order by sum(f.fish_amount) desc) `rank`
        , u.name fisher
        , sum(f.fish_amount) fishies
    from fish f
        inner join users u
            on f.fisher_id = u.user_id
    group by f.fisher_id
    order by sum(f.fish_amount)
    limit 10
    """
    result = execute(cmd)
    table = PrettyTable()
    table.field_names = ["rank", "fisher", "fishies"]
    table.add_rows(result)
    await ctx.send("```\n" + str(table) + "```")


@bot.command()
async def fishytimer(ctx):
    result = execute(
        """
        select max(fish_time) max_fish_time
        from fish
        where fisher_id = %(user_id)s
        """,
        {
            "user_id": ctx.message.author.id,
        },
    )
    if result is None:
        await ctx.send("... you haven't fishy-ed❔")

    last_fish_time = result[0][0]
    if (time_to_fish := (datetime.now() - last_fish_time)) < ALLOWED_FISH_TIME_DELTA:
        await ctx.send(
            f"sailor you need to wait {time_to_fish.seconds} seconds to fishy 🕒🎣🕒"
        )
    else:
        await ctx.send(f"you can fishy sailor!! 🚀🎣🚀")


@bot.event
async def on_ready():
    fish = dedent(
        """\
            /"*._         _
        .-*'`    `*-.._.-'/
     < * ))     ,       (
        `*-._`._(__.--*"`.\\\n"""
    )
    print(fish)


if __name__ == "__main__":
    execute(
        """
    create table if not exists fish (
        fisher_id bigint,
        fish_time timestamp,
        fish_amount int not null,
        primary key(fisher_id, fish_time)
        )
    """
    )
    execute(
        """
    create table if not exists users (
        user_id bigint primary key,
        name varchar(255) not null,
        discriminator int not null,
        foreign key (user_id)
            references fish(fisher_id)
        )
    """
    )
    bot.run(os.environ["DISCORD_FISH_TOKEN"])
