import asyncio

import httpx
from nonebot import get_bot, get_plugin_config, require, get_driver, logger
from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata

from .config import Config
from .utils import (
    AutoSave,
    get_homepage_html,
    get_today,
    get_today_contributions,
    check_contributions,
)

require("nonebot_plugin_alconna")
require("nonebot_plugin_apscheduler")
require("nonebot_plugin_localstore")
require("nonebot_plugin_session")

import nonebot_plugin_localstore as store  # noqa: E402
from nonebot_plugin_alconna import (  # noqa: E402
    At,
    Command,
    Text,
    UniMessage,
    Target,
)
from nonebot_plugin_apscheduler import scheduler  # noqa: E402
from nonebot_plugin_session import EventSession  # noqa: E402

__plugin_meta__ = PluginMetadata(
    name="ghtiles",
    description="看看你的 GitHub 瓷砖",
    usage="",
    homepage="https://github.com/Lipraty/nonebot-plugin-ghtiles",
    type="application",
    config=Config,
    extra={
        "license": "MIT",
        "author": "Lipraty",
    },
)

config = get_plugin_config(Config)

driver = get_driver()

_data = AutoSave(
    store.get_data_file("ghtiles", "data.json"),
    initial_data={"on_reminder": {}, "users": {}},
)


# data structure
# {
#     "on_reminder": {
#         "{group_id}": list[{user_id}]
#     },
#     "users": {
#         "{user_id}": {
#             "username": "{username}",
#             "token"?: "{token}"
#         }
#     }
# }


# messages
def tile_msg(username: str, contributions: int):
    logger.debug(
        f"triggered tile_msg, username: {username}, contributions: {contributions}"
    )
    if contributions == 0:
        return UniMessage(f"{username} 今天还没有贴瓷砖")
    else:
        return UniMessage(f"{username} 在 {get_today()} 贴了 {contributions} 个瓷砖")


def winner_msg(username: str, contributions: int):
    return UniMessage(f"今天的瓷砖王是 {username}，贴了 {contributions} 个瓷砖！")


def no_contributions_msg(user_id: list[str]):
    logger.debug(f"triggered no_contributions_msg, user_id: {user_id}")
    msg = UniMessage()
    for id in user_id:
        msg.append(At("user", id))
    msg += Text("懒鬼懒鬼懒鬼！")
    return msg


@scheduler.scheduled_job("cron", hour=23, minute=30, second=0)
async def schedule():
    reminder_users = list(
        set(user for users in _data["on_reminder"].values() for user in users)
    )
    users = {
        user_id: data
        for user_id, data in _data["users"].items()
        if user_id in reminder_users
    }
    logger.debug(f"get users: {users}, reminder_users: {reminder_users}")
    for user_id, user_data in users.items():
        username = user_data["username"]
        contributions = await get_today_contributions(
            await get_homepage_html(username, config.ght_proxy)
        )
        users[user_id]["contributions"] = contributions
        await asyncio.sleep(1)  # avoid rate limit
    logger.debug(f"users updated of contributions: {users}")
    bot = get_bot()
    for group_id, user_list in _data["on_reminder"].items():
        if not user_list:  # private, skip
            continue
        max_in_group = max(users[user_id]["contributions"] for user_id in user_list)
        max_in_group_username: str = [
            user_id
            for user_id in user_list
            if users[user_id]["contributions"] == max_in_group
        ][0]
        zero_in_group = [
            user_id for user_id in user_list if users[user_id]["contributions"] == 0
        ]
        await UniMessage(
            winner_msg(
                _data["users"].get(max_in_group_username)["username"], max_in_group
            )
        ).send(Target(group_id, platform=bot.adapter.get_name()))
        logger.debug(f"send winner_msg to {group_id}, winner: {max_in_group_username}")
        if zero_in_group:
            await UniMessage(no_contributions_msg(zero_in_group)).send(
                Target(group_id, platform=bot.adapter.get_name())
            )
            logger.debug(
                f"send no_contributions_msg to {group_id}, users: {zero_in_group}"
            )


tile_cmd = (
    Command("tile", "获取 GitHub 瓷砖")
    .alias("瓷砖")
    .usage("tile, 获取今天的 GitHub 瓷砖")
    .build()
)


@tile_cmd.handle()
async def tile_cmd_handle(event: Event, session: EventSession):
    user_id = session.id1
    logger.debug(f"triggered tile_cmd_handle, user_id: {user_id}")
    user_id = _data["users"].get(user_id)
    if not user_id:
        await tile_cmd.finish(
            "好像没有绑定过 GitHub? 输入 `/tile.bind <github username>` 来绑定"
        )
    username = user_id["username"]
    logger.debug(f"triggered tile_cmd_handle, user_id: {user_id}, username: {username}")
    contributions = await get_today_contributions(
        await get_homepage_html(username, config.ght_proxy)
    )
    logger.debug(f"get contributions: {contributions} of {username}")
    await tile_msg(username, contributions).send(event)


tile_bind_cmd = (
    Command("tile.bind <username:str>", "绑定 GitHub 用户名")
    .alias("绑定")
    .usage("tile.bind <username>, 绑定 GitHub 用户名")
    .build()
)


@tile_bind_cmd.handle()
async def tile_bind_cmd_handle(event: Event, username: str, session: EventSession):
    user_id = session.id1
    # check
    if user_id in _data["users"]:
        logger.debug(f"binded user_id: {user_id}")
        return await UniMessage("你已经绑定过了").send(event)
    # check username
    try:
        if not await check_contributions(
            gh_html=await get_homepage_html(username, config.ght_proxy)
        ):
            logger.debug(f"username: {username} has no public activity")
            return await UniMessage("这个用户没有公开活动").send(event)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.debug(f"username: {username} not exists")
            return await UniMessage("这个用户不存在").send(event)
    users_copy = _data["users"].copy()

    user_info = users_copy.get(user_id, {})

    user_info["username"] = username
    users_copy[user_id] = user_info

    _data["users"] = users_copy
    logger.debug(f"binded username: {username} to user_id: {user_id}")
    return await UniMessage(f"绑定成功，你的 GitHub 用户名是 {username}").send(event)


tile_remine_cmd = (
    Command("tile.remind")
    .alias("创建提醒")
    .usage("tile.remind, 创建提醒，每天 23:30 发送")
    .build()
)


@tile_remine_cmd.handle()
async def tile_remine_cmd_handle(event: Event, session: EventSession):
    user_id = session.id1
    group_id = session.id2

    on_reminder_updated = _data["on_reminder"].copy()

    if group_id not in on_reminder_updated:
        on_reminder_updated[group_id] = []

    if user_id in on_reminder_updated[group_id]:
        return await UniMessage("你已经创建过提醒了").send(event)

    on_reminder_updated[group_id].append(user_id)
    _data["on_reminder"] = on_reminder_updated
    logger.debug(f"create reminder for user_id: {user_id} in group_id: {group_id}")
    return await UniMessage("创建提醒成功").send(event)
