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

<a href="./LICENSE">
  <img src="https://img.shields.io/github/license/lgc2333/nonebot-plugin-akinator.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-akinator">
  <img src="https://img.shields.io/pypi/v/nonebot-plugin-akinator.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
<a href="https://pypi.python.org/pypi/nonebot-plugin-akinator">
  <img src="https://img.shields.io/pypi/dm/nonebot-plugin-akinator" alt="pypi download">
</a>
<a href="https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/72301ebc-2fc2-49f9-8b6f-92c19d6bf784">
  <img src="https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/72301ebc-2fc2-49f9-8b6f-92c19d6bf784.svg" alt="wakatime">
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

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

|        配置项         | 必填 | 默认值  |                          说明                          |
| :-------------------: | :--: | :-----: | :----------------------------------------------------: |
|        `PROXY`        |  否  |   无    |                访问 Akinator 使用的代理                |
| `AKINATOR_CHILD_MODE` |  否  | `False` | 是否启用 Akinator 的儿童模式（结果不会出现 NSFW 人物） |
|  `AKINATOR_LANGUAGE`  |  否  |  `cn`   |                    Akinator 的语言                     |

## 🎉 使用

发送指令 `akinator` / `aki` 即可开始游戏

开始游戏后，直接发送你的答案即可（序号和文字均可）

### 效果图

<details>
  <summary>点击展开</summary>

![Alt text](readme/QQ%E5%9B%BE%E7%89%8720230415063509.png)  
![Alt text](readme/QQ%E5%9B%BE%E7%89%8720230415063607.png)

</details>

## 📞 联系

QQ：3076823485  
Telegram：[@lgc2333](https://t.me/lgc2333)  
吹水群：[1105946125](https://jq.qq.com/?_wv=1027&k=Z3n1MpEp)  
邮箱：<lgc2333@126.com>

## 💡 鸣谢

### [Infiniticity/akinator.py](https://github.com/Infiniticity/akinator.py)

- Akinator API 的封装

### [MeetWq/pil-utils](https://github.com/MeetWq/pil-utils/)

- Pillow 工具库

## 💰 赞助

感谢大家的赞助！你们的赞助将是我继续创作的动力！

- [爱发电](https://afdian.net/@lgc2333)
- <details>
    <summary>赞助二维码（点击展开）</summary>

  ![讨饭](https://raw.githubusercontent.com/lgc2333/ShigureBotMenu/master/src/imgs/sponsor.png)

  </details>

## 📝 更新日志

芝士刚刚发布的插件，还没有更新日志的说 qwq~
