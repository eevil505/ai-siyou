#!/usr/bin/env python3
"""AI私邮 — 启用 GitHub Pages（改进自 clock-github 子午流注 enable_pages.py）
用法: GH_TOKEN=<token> python3 enable_pages.py <repo_name>
说明: token 从环境变量 GH_TOKEN 读取；branch 默认 main / 根目录。
"""
import os, sys, urllib.request, json, time

TOKEN = os.environ.get("GH_TOKEN", "")
if not TOKEN:
    print("❌ 缺少 GH_TOKEN 环境变量"); sys.exit(1)

repo = sys.argv[1] if len(sys.argv) > 1 else "ai-siyou"
OWNER = "eevil505"

data = json.dumps({"source": {"branch": "main", "path": "/"}}).encode("utf-8")
req = urllib.request.Request(
    f"https://api.github.com/repos/{OWNER}/{repo}/pages",
    data=data, method="POST",
    headers={"Authorization": f"token {TOKEN}", "Content-Type": "application/json",
             "Accept": "application/vnd.github.v3+json"}
)
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        r = json.loads(resp.read().decode())
        print(f"✅ GitHub Pages 已开启: https://{OWNER}.github.io/{repo}/")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    if e.code == 409:
        print(f"ℹ️ Pages 可能已开启（409 冲突）→ 稍后 curl 验证")
    else:
        print(f"❌ 开启失败 HTTP {e.code}: {body[:300]}"); sys.exit(1)

# 等待 Pages 构建（最多 60 秒）
print("等待 Pages 构建...")
for i in range(12):
    time.sleep(5)
    try:
        req2 = urllib.request.Request(
            f"https://api.github.com/repos/{OWNER}/{repo}/pages",
            headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"})
        with urllib.request.urlopen(req2, timeout=10) as resp2:
            r2 = json.loads(resp2.read().decode())
            if r2.get("status") == "built":
                print(f"✅ Pages 已构建: https://{OWNER}.github.io/{repo}/")
                break
    except Exception:
        pass
else:
    print("⏳ 构建状态未确认，稍后手动验证 URL")
