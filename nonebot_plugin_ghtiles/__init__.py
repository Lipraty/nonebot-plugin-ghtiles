import time
from nonebot import get_bot, get_plugin_config, require, get_driver
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Event

from nonebot_plugin_ghtiles.utils import (
    AutoSave,
    get_homepage_html,
    get_today,
    get_today_contributions,
    check_contributions
)
from .config import Config

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
from nonebot_plugin_session import EventSession, SessionIdType  # noqa: E402

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


# messages
def tile_msg(username: str, contributions: int):
    if contributions == 0:
        return UniMessage(f"{username} 还没有贴瓷砖")
    else:
        return UniMessage(f"{username} 在 {get_today()} 贴了 {contributions} 个瓷砖")


def winner_msg(username: str, contributions: int):
    return UniMessage(f"今天的瓷砖王是 {username}，贴了 {contributions} 个瓷砖！")


def no_contributions_msg(user_id: list[str]):
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
    for user_id, user_data in users.items():
        username = user_data["username"]
        contributions = await get_today_contributions(
            username, await get_homepage_html(username, config.ght_proxy)
        )
        users[user_id]["contributions"] = contributions
        time.sleep(1)  # avoid rate limit
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
        await UniMessage(winner_msg(max_in_group_username, max_in_group)).send(
            Target(group_id, platform=bot.adapter.get_name())
        )
        if zero_in_group:
            await UniMessage(no_contributions_msg(zero_in_group)).send(
                Target(group_id, platform=bot.adapter.get_name())
            )


driver = get_driver()
_data = AutoSave(store.get_data_file("ghtiles", "data.json"))
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

tile_cmd = Command("tile").alias("瓷砖").build()
@tile_cmd.handle()
async def tile_cmd_handle(event: Event, session: EventSession):
    user_id = session.id1
    username = _data[user_id]["username"]
    contributions = await get_today_contributions(
        username, await get_homepage_html(username, config.ght_proxy)
    )
    return await tile_msg(username, contributions).send(event)


tile_bind_cmd = Command("tile.bind <username:str>", "绑定 GitHub 用户名").alias("绑定").build()
@tile_bind_cmd.handle()
async def tile_bind_cmd_handle(event: Event, username: str, session: EventSession):
    user_id = session.id1
    # check
    if user_id in _data["users"]:
        return await UniMessage("你已经绑定过了").send(event)
    # check username
    if check_contributions(username, await get_homepage_html(username, config.ght_proxy)):
        return await UniMessage("这个用户不存在或者没有公开活动").send(event)
    _data["users"][user_id] = {"username": username}
    return await UniMessage(f"绑定成功，你的 GitHub 用户名是 {username}").send(event)


tile_remine_cmd = Command("tile.remind").alias("创建提醒").build()
@tile_remine_cmd.handle()
async def tile_remine_cmd_handle(event: Event, session: EventSession):
    user_id = session.id1
    group_id = session.id2
    if group_id not in _data["on_reminder"].keys():
        _data["on_reminder"][group_id] = []
    if user_id in _data["on_reminder"][group_id]:
        return await UniMessage("你已经创建过提醒了").send(event)
    _data["on_reminder"][group_id].append(user_id)
    return await UniMessage("创建提醒成功").send(event)
