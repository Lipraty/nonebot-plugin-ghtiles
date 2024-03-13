<div align="center">
  <a href="https://v2.nonebot.dev/store">
    <img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/nbp_logo.png" width="180" height="180" alt="logo">
  </a>
  <br>
  <p>
    <img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/NoneBotPlugin.svg" width="240" alt="logo">
  </p>
</div>

<div align="center">

# NoneBot-Plugin-GHTiles

_✨ 看看你的 GitHub 瓷砖 for NoneBot2 ✨_

<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
<a href="https://pdm.fming.dev">
  <img src="https://img.shields.io/badge/pdm-managed-blueviolet" alt="pdm-managed">
</a>

<br />

<a href="https://pydantic.dev">
  <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/pyd-v1-or-v2.json" alt="Pydantic Version 1 Or 2" >
</a>
<a href="./LICENSE">
  <img src="https://img.shields.io/github/license/lipraty/nonebot-plugin-ghtiles.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-ghtiles">
  <img src="https://img.shields.io/pypi/v/nonebot-plugin-ghtiles.svg" alt="pypi">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-ghtiles">
  <img src="https://img.shields.io/pypi/dm/nonebot-plugin-ghtiles" alt="pypi download">
</a>

</div>

## 📖 介绍

NoneBot2 插件，用于查看你的 GitHub 瓷砖

## 💿 安装

以下提到的方法 任选**其一** 即可

<details open>
<summary>[推荐] 使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```bash
nb plugin install nonebot-plugin-ghtiles
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

```bash
pip install nonebot-plugin-ghtiles
```

</details>
<details>
<summary>pdm</summary>

```bash
pdm add nonebot-plugin-ghtiles
```

</details>
<details>
<summary>poetry</summary>

```bash
poetry add nonebot-plugin-ghtiles
```

</details>
<details>
<summary>conda</summary>

```bash
conda install nonebot-plugin-ghtiles
```

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分的 `plugins` 项里追加写入

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_picstatus"
]
```

</details>

## ⚙️ 配置

#### `ght_proxy`

- **类型**: `str`
- **默认值**: `"https://github.com"`

GitHub 地址，如果需要解决国内访问 GitHub 的问题，可以替换为镜像站点

## 🎉 使用

### 指令

#### `tile`

查看你的 GitHub 瓷砖

#### `tile.bind <username>`

绑定你的 GitHub 用户名

#### `tile.remine`

创建一个提醒，当这一天即将过去而你还没有提交时，会提醒你

## 💡 鸣谢

### [nonebot/plugin-alconna](https://github.com/nonebot/plugin-alconna)

- 强大的命令解析库，和多平台适配方案
