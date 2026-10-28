#!/usr/bin/env python3
"""BumpAPI 客户端接入示例。零依赖，只用标准库。

用法：
    python check_update.py --current 1.0.0
    python check_update.py --app-key app_xxx --current 1.0.0

app_key 也可以放在环境变量 BUMP_APP_KEY 里。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = "https://bump.tinyaii.cn/api/v1/check"
TIMEOUT = 3.0


class AppKeyNotFound(Exception):
    """app_key 不存在。这是开发者配置问题，应该修代码，不是打扰终端用户。"""


def check_update(app_key: str, current_version: str) -> dict | None:
    """查询是否有新版本。

    返回 None 表示查不到（断网、超时、服务异常、返回不是 JSON）。
    调用方应当把 None 当成「没有更新」，不要弹错误框。

    app_key 不存在时抛 AppKeyNotFound —— 这种错误只会在开发阶段出现，
    上线后不该发生，所以单独抛出来，方便你第一时间发现配置错了。
    """
    query = urllib.parse.urlencode(
        {"app_key": app_key, "current_version": current_version}
    )
    try:
        with urllib.request.urlopen(f"{ENDPOINT}?{query}", timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise AppKeyNotFound(app_key) from None
        return None
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 BumpAPI 上有没有新版本")
    parser.add_argument(
        "--app-key",
        default=os.environ.get("BUMP_APP_KEY", ""),
        help="应用标识，也可以用环境变量 BUMP_APP_KEY",
    )
    parser.add_argument("--current", default="1.0.0", help="客户端当前版本号")
    args = parser.parse_args()

    if not args.app_key:
        print("缺少 app_key：用 --app-key 或环境变量 BUMP_APP_KEY 传入", file=sys.stderr)
        return 2

    try:
        info = check_update(args.app_key, args.current)
    except AppKeyNotFound:
        print(
            f"app_key 不存在：{args.app_key}\n"
            "去 https://bump.tinyaii.cn/app/ 复制正确的 key。这是配置错误，不是用户能解决的问题。",
            file=sys.stderr,
        )
        return 1

    if info is None:
        print("查询失败（网络或服务异常）—— 按「没有更新」处理，不打扰用户")
        return 0

    if not info.get("has_update"):
        print(f"已是最新版本（{args.current}）")
        return 0

    print(f"发现新版本：{info.get('latest_version')}")
    if notes := info.get("release_notes"):
        print(f"更新说明：{notes}")
    if published := info.get("publish_time"):
        print(f"发布时间：{published}")
    if url := info.get("download_url"):
        print(f"下载地址：{url}")

    if info.get("force_update"):
        print("[强制更新] 用户不能跳过，必须升级后才能继续使用")
    else:
        print("[可选更新] 用户可以选择稍后")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
