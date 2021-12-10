"""fishy <==3"""
from __future__ import annotations

import asyncio
import html
import logging
import random
import os
import re
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypedDict

import discord
from discord.ext import commands
from discord.utils import escape_markdown

Context = discord.ext.commands.context.Context


bot = commands.Bot(command_prefix="$")

@bot.command()
async def fishy(ctx: Context) -> None:
    """Fishhy"""
    await ctx.send(f"you caught {random.randrange(1001)} fishy 🐟")


if __name__ == "__main__":
    bot.run("OTE4OTk2OTI3OTgxNDI0NjQw.YbPYlQ.oKQNxw2xIHaGqoRMHWOghUootjE")#(os.environ["DISCORDFISH_TOKEN"])
