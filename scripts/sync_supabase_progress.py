#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_supabase_progress.py —— 按实际进度同步 Supabase 数据库（weeks/topics 状态）。

只 UPDATE 不 TRUNCATE：保留 notes、IDs 和既有关联。幂等，可重复执行。

历史状态快照（2026-08-05 确认；课程标题和主题后来已调整，执行前必须重新审核）：
- week 6（7.27-8.2 最小业务闭环）→ done，7 个 topics 全 completed
- week 7（8.3-8.9）→ done，7 个 topics 全 completed
- week 8（8.10-8.16）→ active，0 个 topics completed
- week 9-12 → pending（不变）

本脚本会修改远程 Supabase 数据。不得因为本地课程标题调整而直接运行；
必须先获得用户对数据库更新的单独授权，并核对脚本中的更新范围。
"""
import json
import os
import re
import sys
import time
import urllib.request

# 代理只从标准环境变量读取；未配置时使用系统默认网络。
PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
_opener = (
    urllib.request.build_opener(urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))
    if PROXY
    else urllib.request.build_opener()
)

# 读 config.js（仓库内配置，含 URL 与 publishable key）
cfg_src = open("config.js", encoding="utf-8").read()
def grab(key):
    m = re.search(key + r":\s*'([^']+)'", cfg_src)
    if not m:
        raise RuntimeError(f"config.js 缺少 {key}")
    return m.group(1)
SUPABASE_URL = grab("SUPABASE_URL")
SUPABASE_KEY = grab("SUPABASE_KEY")

BASE = SUPABASE_URL + "/rest/v1"


def api(path, method="GET", payload=None, retries=3):
    req = urllib.request.Request(BASE + path, method=method, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": "Bearer " + SUPABASE_KEY,
        "Content-Type": "application/json",
    })
    data = json.dumps(payload).encode() if payload is not None else None
    last_err = None
    for attempt in range(retries):
        try:
            with _opener.open(req, data=data, timeout=25) as resp:
                body = resp.read().decode()
                return json.loads(body) if body else None
        except Exception as e:
            last_err = e
            print(f"  [retry {attempt + 1}/{retries}] {e.__class__.__name__}: {str(e)[:80]}")
            time.sleep(2)
    raise RuntimeError(f"Supabase 请求失败: {path}: {last_err}")


def main() -> int:
    # 1. 查询当前 weeks
    weeks = api("/weeks?select=id,week_number,status&order=week_number")
    by_number = {w["week_number"]: w for w in weeks}
    print(f"数据库 weeks 共 {len(weeks)} 条")

    # 2. 更新 weeks 状态
    week_status = {
        6: "done", 7: "done", 8: "active",
        9: "pending", 10: "pending", 11: "pending", 12: "pending",
    }
    for num, status in week_status.items():
        w = by_number.get(num)
        if not w:
            print(f"  [warn] week {num} 不存在，跳过")
            continue
        if w["status"] != status:
            api(f"/weeks?id=eq.{w['id']}", method="PATCH",
                payload={"status": status})
            print(f"  [ok] week {num}: {w['status']} -> {status}")
        else:
            print(f"  week {num} 已是 {status}，跳过")

    # 3. 更新 week 6/7 的 topics 为 completed
    for num in (6, 7):
        w = by_number.get(num)
        if not w:
            continue
        topics = api(f"/topics?week_id=eq.{w['id']}&select=id,completed")
        n = 0
        for t in topics:
            if not t["completed"]:
                api(f"/topics?id=eq.{t['id']}", method="PATCH",
                    payload={"completed": True})
                n += 1
        print(f"  [ok] week {num}: {n} 个 topic 置为 completed（共 {len(topics)} 个）")

    print("\n✅ Supabase 进度同步完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
