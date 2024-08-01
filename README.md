<!-- markdownlint-disable MD031 MD033 MD036 MD041 -->

<div align="center">

<a href="https://v2.nonebot.dev/store">
  <img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo">
</a>

<p>
  <img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText">
</p>

# NoneBot-Plugin-Akinator

_✨ 网络天才 ✨_

<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
<a href="https://pdm.fming.dev">
  <img src="https://img.shields.io/badge/pdm-managed-blueviolet" alt="pdm-managed">
</a>
<a href="https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/72301ebc-2fc2-49f9-8b6f-92c19d6bf784">
  <img src="https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/72301ebc-2fc2-49f9-8b6f-92c19d6bf784.svg" alt="wakatime">
</a>

<br />

<a href="https://pydantic.dev">
  <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/pyd-v1-or-v2.json" alt="Pydantic Version 1 Or 2" >
</a>
<a href="./LICENSE">
  <img src="https://img.shields.io/github/license/lgc-NB2Dev/nonebot-plugin-akinator.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-akinator">
  <img src="https://img.shields.io/pypi/v/nonebot-plugin-akinator.svg" alt="pypi">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-akinator">
  <img src="https://img.shields.io/pypi/dm/nonebot-plugin-akinator" alt="pypi download">
</a>

</div>

## 📖 介绍

把网络天才 Akinator 搬进你的 Bot !

## 💿 安装

以下提到的方法 任选**其一** 即可

<details open>
<summary>[推荐] 使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```bash
nb plugin install nonebot-plugin-akinator
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

```bash
pip install nonebot-plugin-akinator
```

</details>
<details>
<summary>pdm</summary>

```bash
pdm add nonebot-plugin-akinator
```

</details>
<details>
<summary>poetry</summary>

```bash
poetry add nonebot-plugin-akinator
```

</details>
<details>
<summary>conda</summary>

```bash
conda install nonebot-plugin-akinator
```

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分的 `plugins` 项里追加写入

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_akinator"
]
```

</details>

## ⚙️ 配置

在 nonebot2 项目的 `.env` 文件中添加下表中的必填配置

|            配置项            | 必填 | 默认值  |                          说明                          |
| :--------------------------: | :--: | :-----: | :----------------------------------------------------: |
|           `PROXY`            |  否  |   无    |                访问 Akinator 使用的代理                |
|    `AKINATOR_CHILD_MODE`     |  否  | `False` | 是否启用 Akinator 的儿童模式（结果不会出现 NSFW 人物） |
|     `AKINATOR_LANGUAGE`      |  否  |  `cn`   |                    Akinator 的语言                     |
|     `AKINATOR_TEXT_MODE`     |  否  |  `cn`   |                    是否启用文字模式                    |
| `AKINATOR_OPERATION_TIMEOUT` |  否  |  `cn`   |               插件等待消息回复的超时时间               |
|  `AKINATOR_REQUEST_TIMEOUT`  |  否  |  `cn`   |                 插件网络请求的超时时间                 |

## 🎉 使用

发送指令 `akinator` / `aki` 即可开始游戏

开始游戏后，直接发送你的答案即可（序号和文字均可）

如果 `htmlrender` 依赖已安装，默认将会渲染图片，如果没有则会回退到文本模式

### 效果图

<details open>
  <summary>点击展开/收起</summary>

#### 文本模式

![文本模式](https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/akinator/QQ20240802-001216.png)

#### 图片模式

![图片模式](https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/akinator/QQ20240802-000937.png)

</details>

## 📞 联系

QQ：3076823485  
Telegram：[@lgc2333](https://t.me/lgc2333)  
吹水群：[1105946125](https://jq.qq.com/?_wv=1027&k=Z3n1MpEp)  
邮箱：<lgc2333@126.com>

## 💡 鸣谢

### [lgc2333/cooaki](https://github.com/lgc2333/cooaki)

- Akinator API 的封装

### [MeetWq/pil-utils](https://github.com/MeetWq/pil-utils/)

- Pillow 工具库

## 💰 赞助

**[赞助我](https://blog.lgc2333.top/donate)**

感谢大家的赞助！你们的赞助将是我继续创作的动力！

## 📝 更新日志

### 1.0.1

- 修复 htmlrender 依赖不是可选的 bug
- 修复不会自动撤回游戏结束前一条问题消息的 Bug

### 1.0.0

- 插件重构：
  - 整体代码重构，换用自己写的 API 包装库，使用 htmlrender 渲染图片，同时支持文本模式
  - 配置项改动：
    - 新增 `AKINATOR_TEXT_MODE`
    - 新增 `AKINATOR_OPERATION_TIMEOUT`
    - 新增 `AKINATOR_REQUEST_TIMEOUT`

### 0.2.0

- 适配 Pydantic V1 & V2
- 换用 alconna

### 0.1.3

- 支持更多平台
- 删除猜出角色后继续猜的功能，因为有 Bug
