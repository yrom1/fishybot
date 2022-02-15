from __future__ import annotations

import asyncio
import math
import os
import random
import sys
import warnings
from configparser import ConfigParser
from datetime import datetime, timedelta
from functools import wraps
from textwrap import dedent
from typing import Any, Callable, Dict, List, Optional, Tuple, TypedDict, Union

import aiomysql
import discord
from discord import user
from discord.ext import commands
from discord.utils import escape_markdown
from prettytable import PrettyTable

FISH = """\
        /"*._         _
    .-*'`    `*-.._.-'/
< * ))     ,       (
    `*-._`._(__.--*"`.\\
"""

INTENTS = discord.Intents.default()
INTENTS.members = True
bot = commands.Bot(
    command_prefix="$", intents=INTENTS
)  # bot is conventionally lowercase
# time delta must be >= 1 to insert into fish table with unique key
ALLOWED_FISH_TIME_DELTA = timedelta(seconds=1)

if not sys.warnoptions:
    warnings.simplefilter("ignore")


def config(filename="config.ini", section="mysql") -> Dict[str, str]:
    parser = ConfigParser()
    parser.read(filename)
    config_dict: Dict[str, str] = {}
    if parser.has_section(section):
        for item in parser.items(section):
            key, value = item
            config_dict[key] = value
    else:
        raise Exception(f"Section {section} not found in the {filename} file")

    return config_dict


# TODO pooling
async def execute(
    command: str,
    data: Union[Tuple[Any, ...], Dict[Any, Any]] = tuple(),
    rowcount=False,
) -> Union[Tuple[Any, Any], List[Tuple[Any, ...]]]:
    try:
        conn = await aiomysql.connect(**config())
        cursor = await conn.cursor()
        await cursor.execute(command, data)
        if rowcount:
            num_rows = cursor.rowcount
        result = await cursor.fetchall()
        await conn.commit()

    except Exception as e:
        if not None:
            print(f"{command=}")
        raise e

    finally:
        await cursor.close()
        conn.close()

    if rowcount:
        return result, num_rows
    return result


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


@bot.command(
    aliases=["fosh", "fish", "fihy", "fisy", "foshy", "fisyh", "fsihy", "fin", "ifhs"]
)
async def fishy(ctx, user: discord.Member = None):
    """Go fishing"""

    catch = random.choices(list(FISHTYPES.keys()), WEIGHTS)[0]
    fish_amount = FISHTYPES[catch]()

    gift = False
    gifted_user_id = None
    if user is not None and user.id != ctx.message.author.id:
        await ctx.send(
            f"a gift from {ctx.message.author.mention} to {user.mention} :heart:"
        )
        gift = True
        gifted_user_id = user.id
    elif user is not None and user.id == ctx.message.author.id:
        await ctx.send(f"cant gift fish to yourself idiot")
        return

    _, insert_row_count = await execute(
        """
        insert into fish (fisher_id, fish_time, fish_amount, gift, gifted_user_id)
        select %(author_id)s, now(), %(fish_amount)s, %(gift)s, %(gifted_user_id)s
        from fish
        where fisher_id = %(discord_id)s
        having not exists (select %(author_id)s from fish)
            or time_to_sec(timediff(now(), max(fish_time)) > 10
        """,
        tuple(
            {
                'author_id': ctx.message.author.id,
                'fish_amount': fish_amount,
                'gift': gift,
                'gifted_user_id': gifted_user_id,
            }
        ),
        rowcount=True,
    )

    if insert_row_count != 1:
        query_time_to_next_fish = await execute(
            """
        select 10 - time_to_sec(timediff(now(), max(fish_time)))
        from fish
        where fisher_id = %(discord_id)s
        """,
            {
                "discord_id": ctx.message.author.id,
            },
        )

        time_to_next_fish = (lambda x: 1 if x < 1 else x)(query_time_to_next_fish[0][0])

        await ctx.send(f"too fast sailor 🏃 can fish in {time_to_next_fish} seconds 🎣")
        return

    await execute(
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

    if gift and user is not None:
        await execute(
            """
            INSERT INTO users (user_id, name, discriminator)
            VALUES (%(user_id)s, %(name)s, %(discriminator)s)
            ON DUPLICATE KEY UPDATE
                name = %(name)s,
                discriminator = %(discriminator)s
            """,
            {
                "user_id": user.id,
                "name": user.name,
                "discriminator": user.discriminator,
            },
        )

    if fish_amount == 0:
        await ctx.send(f"you caught trash {random.choice(TRASH_ICONS)}")
    else:
        if catch == "common":
            fish_emoji = random.choice(
                [":fish:", ":tropical_fish:", ":blowfish:", ":shrimp:"]
            )
        elif catch == "uncommon":
            fish_emoji = random.choice([":squid:", ":lobster:", ":crab:"])
        elif catch == "rare":
            fish_emoji = random.choice([":dolphin:", ":shark:"])
        else:  # catch == "legendary":
            fish_emoji = random.choice([":whale:", ":whale2:"])

        def fish_emoji_multiplier(fish_amount: int) -> str:
            return (lambda x: fish_emoji if x == "" else x)(
                fish_emoji * int(fish_amount // 10)
            )

        if catch == "common" or catch == "uncommon":
            catch_string = f"you caught {fish_amount} {catch} fishy {fish_emoji_multiplier(fish_amount)}"
            await ctx.send(catch_string)
        elif catch == "rare":
            catch_string = f"**:star: you caught {fish_amount} {catch} fishy :star: {fish_emoji_multiplier(fish_amount)}**"
            await ctx.send(catch_string)
        else:  # catch == "legendary":
            catch_string = f"**:star2: you caught {fish_amount} {catch} fishy :star2: {fish_emoji_multiplier(fish_amount)}**"
            await ctx.send(catch_string)


@bot.command(aliases=["globalfishstats", "globalfishysta", "globalfishystast"])
async def globalfishystats(ctx):
    """Fishing leaderboard"""
    query_global_count = await execute("select sum(fish_amount) from fish f")
    query_global_count = query_global_count[0][0]
    query_fish_type_count = await execute(
        """
    with cte as(
    select fisher_id
        , fish_amount
    from fish
    where gift = 0
    union all
    select gifted_user_id fisher_id
        , fish_amount
    from fish
    where gift = 1
    )
    , total_fishies as(
    select fisher_id
        , sum(fish_amount) fishies
    from cte
    group by fisher_id
    order by sum(fish_amount) desc
    )
    select concat_ws('#', u.name, u.discriminator) fisher
        , fishies
    from users u
        left join total_fishies tf
            on u.user_id = tf.fisher_id
    order by fishies desc
    """
    )
    table = PrettyTable()
    table.field_names = [
        "fisher",
        "fishies",
    ]
    table.add_rows(query_fish_type_count)
    if query_fish_type_count is not None and query_global_count is not None:
        await ctx.send(
            f"{query_global_count} digital fishy fished 🎣\n"
            "global 🌎 results include gifts 🎁\n```\n" + str(table) + "```"
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
async def fishystats(ctx):
    """Your fish total and type stats"""
    query_has_fished_before = await execute(
        """
        select exists(
        select *
        from fish
        where fisher_id = %s
        ) id_exists
        """,
        tuple([ctx.message.author.id]),
    )
    query_has_fished_before = query_has_fished_before[0][0]
    # print(f"{query_has_fished_before}")
    if not query_has_fished_before:
        await ctx.send("you need to fish once to have stats! 📊")
        return

    query_fish_sum = await execute(
        """
        select sum(fish_amount)
        from fish
        where fisher_id = %s
            and gift = false
        """,
        tuple([ctx.message.author.id]),
    )
    query_fish_sum = query_fish_sum[0][0]
    query_fish_type_count = await execute(
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
        and gift = false
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
            f"you've fished {query_fish_sum} digital fishy 🎣\n"
            "```\n" + str(table) + "```"
        )


@bot.command()
async def fishytimer(ctx):
    """Time to next fishy"""
    result = await execute(
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


@bot.command()
async def up(ctx):
    """Is bot up?"""
    await ctx.send("up! 🐠")


@bot.event
async def on_ready():
    print(FISH)


if __name__ == "__main__":

    async def setup() -> None:
        await execute(
            """
        create table if not exists users (
            user_id bigint primary key,
            name varchar(255) not null,
            discriminator int not null
            )
        """
        )
        await execute(
            """
        create table if not exists fish (
            fisher_id bigint,
            fish_time timestamp,
            fish_amount int not null,
            gift tinyint default 0 not null,
            gifted_user_id bigint default null,
            primary key(fisher_id, fish_time),
            foreign key (fisher_id)
                references users(user_id)
            )
        """
        )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    bot.run(os.environ["DISCORD_FISH_TOKEN"])
