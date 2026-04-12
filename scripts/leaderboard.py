#!/usr/bin/env python3
"""
酒量排行榜自动生成脚本

通过 GitHub API 统计每个贡献者的酒量（积分），
按 Issue 类型和 PR label 计算分值，生成 LEADERBOARD.md。

用法：
    GITHUB_TOKEN=xxx python scripts/leaderboard.py

需要环境变量：
    GITHUB_TOKEN — GitHub Personal Access Token（需要 repo 读权限）
"""

import json
import os
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

REPO = "tiaohai-drinknjump/tiaohai-community-skill"
API_BASE = f"https://api.github.com/repos/{REPO}"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

# 酒量分值表
SCORES = {
    "issue_data": 5,
    "issue_social_good": 10,
    "issue_bug": 10,
    "issue_new_city": 5,
    "pr_merged_data": 20,
    "pr_merged_content": 30,
    "pr_merged_social_good": 40,
    "pr_merged_bartender_story": 50,
    "pr_merged_rfc": 15,
    "pr_merged_default": 20,
    "review": 10,
}

# Issue label → 分值类型映射
ISSUE_LABEL_MAP = {
    "data-update": "issue_data",
    "social-good": "issue_social_good",
    "bug": "issue_bug",
    "new-city": "issue_new_city",
}

# PR label → 分值类型映射
PR_LABEL_MAP = {
    "data-update": "pr_merged_data",
    "social-good": "pr_merged_social_good",
    "content": "pr_merged_content",
    "bartender-story": "pr_merged_bartender_story",
    "rfc": "pr_merged_rfc",
}

# 徽章条件
BADGE_THRESHOLDS = {
    "🐱 跳跳的朋友": lambda s: s.get("social_good_contributions", 0) >= 1,
    "🎸 驻场乐手": lambda s: s.get("content_contributions", 0) >= 5,
    "🔧 建筑师": lambda s: s.get("rfc_contributions", 0) >= 1,
    "📖 说书人": lambda s: s.get("story_contributions", 0) >= 1,
    "🍺 璀璨钻石": lambda s: s.get("total", 0) >= 500,
}


def api_get(path, params=None):
    url = f"{API_BASE}/{path}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(url)
    if TOKEN:
        req.add_header("Authorization", f"token {TOKEN}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"API error: {e}")
        return []


def get_all_pages(path, params=None):
    if params is None:
        params = {}
    params["per_page"] = "100"
    page = 1
    all_items = []
    while True:
        params["page"] = str(page)
        items = api_get(path, params)
        if not items:
            break
        all_items.extend(items)
        if len(items) < 100:
            break
        page += 1
    return all_items


def calculate_scores():
    scores = defaultdict(lambda: defaultdict(int))

    # Closed issues (by author)
    issues = get_all_pages("issues", {"state": "closed", "filter": "all"})
    for issue in issues:
        if issue.get("pull_request"):
            continue  # skip PRs
        user = issue["user"]["login"]
        labels = [l["name"] for l in issue.get("labels", [])]
        score_type = "issue_data"
        for label, stype in ISSUE_LABEL_MAP.items():
            if label in labels:
                score_type = stype
                break
        scores[user]["total"] += SCORES[score_type]
        if score_type == "issue_social_good":
            scores[user]["social_good_contributions"] += 1

    # Merged PRs
    pulls = get_all_pages("pulls", {"state": "closed"})
    for pr in pulls:
        if not pr.get("merged_at"):
            continue
        user = pr["user"]["login"]
        labels = [l["name"] for l in pr.get("labels", [])]
        score_type = "pr_merged_default"
        for label, stype in PR_LABEL_MAP.items():
            if label in labels:
                score_type = stype
                break
        scores[user]["total"] += SCORES[score_type]
        if "social-good" in labels:
            scores[user]["social_good_contributions"] += 1
        if "content" in labels:
            scores[user]["content_contributions"] += 1
        if "rfc" in labels:
            scores[user]["rfc_contributions"] += 1
        if "bartender-story" in labels:
            scores[user]["story_contributions"] += 1
        scores[user]["last_contribution"] = pr.get("title", "")

    # Reviews
    for pr in pulls:
        reviews = api_get(f"pulls/{pr['number']}/reviews")
        if not isinstance(reviews, list):
            continue
        for review in reviews:
            user = review["user"]["login"]
            if review.get("state") in ("APPROVED", "CHANGES_REQUESTED", "COMMENTED"):
                scores[user]["total"] += SCORES["review"]

    return scores


def get_badges(user_scores):
    badges = []
    for badge, condition in BADGE_THRESHOLDS.items():
        if condition(user_scores):
            badges.append(badge)
    return " ".join(badges) if badges else "—"


def generate_leaderboard(scores):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    keepers = []
    bartenders = []
    villagers = []

    for user, s in sorted(scores.items(), key=lambda x: x[1]["total"], reverse=True):
        if user in ("tiaohai-bot", "github-actions[bot]"):
            continue
        total = s["total"]
        badges = get_badges(s)
        last = s.get("last_contribution", "")
        entry = {
            "user": user,
            "total": total,
            "badges": badges,
            "last": last,
        }
        if total >= 3000:
            keepers.append(entry)
        elif total >= 300:
            bartenders.append(entry)
        else:
            villagers.append(entry)

    lines = [
        "# 酒量排行榜",
        "",
        f"> 上次更新：{now}",
        ">",
        "> 每周一自动更新。酒量 = 你在这个数字酒馆留下的痕迹。",
        "",
        "## 👑 掌群人",
        "",
        "| 排名 | 村民 | 酒量 | 徽章 |",
        "|------|------|------|------|",
    ]
    if keepers:
        for i, e in enumerate(keepers, 1):
            lines.append(f"| {i} | @{e['user']} | {e['total']} | {e['badges']} |")
    else:
        lines.append("| — | 虚位以待 | — | — |")

    lines += [
        "",
        "## 🍺 打酒师",
        "",
        "| 排名 | 村民 | 酒量 | 徽章 |",
        "|------|------|------|------|",
    ]
    if bartenders:
        for i, e in enumerate(bartenders, len(keepers) + 1):
            lines.append(f"| {i} | @{e['user']} | {e['total']} | {e['badges']} |")
    else:
        lines.append("| — | 虚位以待 | — | — |")

    lines += [
        "",
        "## 🆕 村民",
        "",
        "| 排名 | 村民 | 酒量 | 最近贡献 |",
        "|------|------|------|---------|",
    ]
    if villagers:
        for i, e in enumerate(villagers, len(keepers) + len(bartenders) + 1):
            lines.append(f"| {i} | @{e['user']} | {e['total']} | {e['last'][:40]} |")
    else:
        lines.append("| — | 虚位以待 | — | — |")

    lines += [
        "",
        "---",
        "",
        "*多一个人站在吧台里面，就会有多 20 个人站在外面。*",
        "",
    ]

    return "\n".join(lines)


def main():
    print("Calculating scores...")
    scores = calculate_scores()
    print(f"Found {len(scores)} contributors")

    md = generate_leaderboard(scores)

    out_path = os.path.join(os.path.dirname(__file__), "..", "LEADERBOARD.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Leaderboard written to {out_path}")


if __name__ == "__main__":
    main()
