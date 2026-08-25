#!/usr/bin/env python3
"""AI私邮 — 创建 GitHub 仓库（改进自 clock-github 子午流注 create_repo.py）
用法: GH_TOKEN=<token> python3 create_repo.py <repo_name> [description]
说明: token 从环境变量 GH_TOKEN 读取，不硬编码（clock-github 旧脚本的教训）。
"""
import os, sys, urllib.request, json

TOKEN = os.environ.get("GH_TOKEN", "")
if not TOKEN:
    print("❌ 缺少 GH_TOKEN 环境变量"); sys.exit(1)

repo = sys.argv[1] if len(sys.argv) > 1 else "ai-siyou"
desc = sys.argv[2] if len(sys.argv) > 2 else "AI私邮 · AI 英语私教落地页（PWA）——邮件交付，1 对 1 陪练"
USERNAME = "eevil505"

data = json.dumps({
    "name": repo,
    "description": desc,
    "homepage": f"https://{USERNAME}.github.io/{repo}",
    "private": False,
    "auto_init": False
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.github.com/user/repos",
    data=data, method="POST",
    headers={"Authorization": f"token {TOKEN}", "Content-Type": "application/json",
             "Accept": "application/vnd.github.v3+json"}
)
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        r = json.loads(resp.read().decode())
        print(f"✅ 仓库创建成功: {r['html_url']}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    if e.code == 422 and "already exists" in body:
        print(f"ℹ️ 仓库已存在（跳过创建）: https://github.com/{USERNAME}/{repo}")
    else:
        print(f"❌ 创建失败 HTTP {e.code}: {body[:300]}"); sys.exit(1)
