# bumpapi-example

用不到 60 行 Python 演示怎么接 [BumpAPI](https://bump.tinyaii.cn) —— 桌面软件的版本检查服务。

零依赖，只用标准库，Python 3.10+。

## 跑起来

```bash
python check_update.py --current 0.9.0
```

```
发现新版本：1.0.4
更新说明：修复
发布时间：2026-10-28
[强制更新] 用户不能跳过，必须升级后才能继续使用
```

换几个版本号看看不同结果：

```bash
python check_update.py --current 1.0.0   # 有更新，可选
python check_update.py --current 1.0.4   # 已是最新
```

仓库里带的 `app_key` 是演示用的，最新版本和阈值随时可能变。

## 三种情况

| 客户端版本 | 返回 |
| --- | --- |
| 0.9.0 | 有更新，`force_update: true` |
| 1.0.0 | 有更新，`force_update: false` |
| 1.0.4 | 无更新 |

## 这个例子示范了什么

1. **3 秒超时** —— 断网时不至于卡住软件启动
2. **任何异常都返回 `None`** —— 调用方按「没有更新」处理，不弹错误框
3. **404 单独抛 `AppKeyNotFound`** —— 这是你的 key 配错了，开发阶段就该炸出来，不要让终端用户看到
4. **`app_key` 从参数或环境变量读** —— 不硬编码，方便打包时注入

第 3 点值得展开：检查更新失败通常分两种，一种是网络问题（用户的地铁、酒店的 WiFi），一种是配置问题（你的 key 写错了）。前者必须静默，后者必须吵醒你，但不能吵醒用户。这两件事混在一起处理，就会出现「用户打开软件弹一个 `app_key not found`」的荒唐场面。

## 换成你自己的

去[控制台](https://bump.tinyaii.cn/app/)注册、建应用，复制 `app_key`：

```bash
BUMP_APP_KEY=app_你的key python check_update.py --current 1.0.0
```

## 接到真实项目里

把 `check_update()` 抄过去，启动时调一次就行：

```python
info = check_update(APP_KEY, CURRENT_VERSION)
if info and info.get("has_update"):
    show_update_dialog(info)  # 你自己的弹窗
```

注意 `if info and ...` —— 查不到时 `info` 是 `None`，直接 `info["has_update"]` 会崩。这就是为什么失败时返回 `None` 而不是空字典：让调用方不得不想一下。

## 别的语言

C#、Python、JavaScript、Go 的完整示例在[接入文档](https://bump.tinyaii.cn/docs/#samples)。BumpAPI 控制台里每个应用还有一个「接入」按钮，会生成带你真实 `app_key` 的代码和一段可以直接丢给 AI 的提示词。

## 许可

MIT
