"""候選風格清單（sources/*.json）的共用函式。CLI 在 scripts/candidates.py。

清單格式：
{
  "channel": {...},
  "videos":     [{"id": "YouTube 影片 ID", "title": "...", "published": "YYYY-MM-DD"}],
  "candidates": [{"name_en": "...", "video": "影片 ID", "t": "1:15",
                  "status": "pending|done|skipped", "style_id": "...", "note": "..."}]
}
"""
import datetime, json, os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SOURCES = os.path.join(ROOT, "sources")
STYLES = os.path.join(ROOT, "styles")
UPDATES = os.path.join(ROOT, "UPDATES.md")
STATUSES = ("pending", "done", "skipped")

_TS = re.compile(r"^\s*((?:\d{1,2}:)?\d{1,2}:\d{2})\s+(.+?)\s*$")
_NOT_STYLE = re.compile(
    r"^(intro|outro|final thoughts?|bonus style|.*\bkittl\b.*|how to .*|where to .*|when to .*"
    r"|\d+ (more )?design (styles?|names?))$", re.I)
_STYLE_VIDEO = re.compile(r"design (styles?|names?)|style trends?|aesthetics? you", re.I)
_SUFFIX = ("design", "style", "aesthetic")


def slug(name):
    s = name.strip().lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def style_key(name):
    """比對用的鍵：去掉結尾的 Design／Style／Aesthetic。"""
    parts = slug(name).split("-")
    while len(parts) > 1 and parts[-1] in _SUFFIX:
        parts.pop()
    return "-".join(parts)


def is_chapter_style(name):
    return not _NOT_STYLE.match(name.strip())


def is_style_video(title):
    return bool(_STYLE_VIDEO.search(title))


def parse_timestamps(description):
    """從 YouTube 說明欄的章節時間軸取出 (時間, 名稱)，排除 Intro 這類非風格章節。"""
    lines = description.splitlines()
    start = next((i + 1 for i, l in enumerate(lines) if "timestamps" in l.lower()), None)
    out = []
    if start is not None:
        for l in lines[start:]:
            m = _TS.match(l)
            if m:
                out.append((m.group(1), m.group(2)))
            elif out and not l.strip():
                break
    else:
        out = [(m.group(1), m.group(2)) for m in map(_TS.match, lines) if m]
        if len(out) < 3:
            out = []
    return [(t, n) for t, n in out if is_chapter_style(n)]


def find(data, name):
    k = style_key(name)
    for c in data["candidates"]:
        if style_key(c["name_en"]) == k or c.get("style_id") == k:
            return c
    return None


def next_pending(data, n):
    return [c for c in data["candidates"] if c["status"] == "pending"][:n]


def mark(data, name, status, style_id=None, note=None, today=None):
    if status not in STATUSES:
        raise ValueError(f"status 只能是 {', '.join(STATUSES)}")
    c = find(data, name)
    if c is None:
        raise KeyError(f"候選清單裡沒有：{name}")
    if status == "done" and not (style_id or c.get("style_id")):
        raise ValueError("標成 done 要給 style_id")
    c["status"] = status
    if style_id:
        c["style_id"] = style_id
    if status == "done":
        c["done_on"] = today or datetime.date.today().isoformat()
    if note:
        c["note"] = note
    return c


SITE = "https://deathscythe1021.github.io/PREMA/"


def next_monday(day):
    d = datetime.date.fromisoformat(day)
    return (d + datetime.timedelta(days=7 - d.weekday())).isoformat()


def render_log(data, names_zh, per_week=3, weeks=8):
    """產生 UPDATES.md：已更新（依日期，新的在上）＋接下來每週預計做哪幾種。

    只依資料計算（排程從最後一次更新的下一個週一算起），同樣的資料一定產生同樣的內容。
    """
    vids = {v["id"]: v["title"] for v in data.get("videos", [])}
    done = [c for c in data["candidates"] if c["status"] == "done" and c.get("done_on")]
    by_day = {}
    for c in done:
        by_day.setdefault(c["done_on"], []).append(c)
    pending = [c for c in data["candidates"] if c["status"] == "pending"]
    n_done = sum(c["status"] == "done" for c in data["candidates"])

    out = ["# 更新紀錄", "",
           "這份檔案由 `python3 scripts/candidates.py log` 依 `sources/kittl.json` 產生，不要手動修改。",
           f"目前已收錄 {n_done} 種 Kittl 風格，待做 {len(pending)} 種。", "",
           "## 已更新", ""]
    for day in sorted(by_day, reverse=True):
        items = by_day[day]
        out.append(f"### {day}（新增 {len(items)} 種）")
        out.append("")
        for c in items:
            sid = c["style_id"]
            zh = names_zh.get(sid, "")
            label = f"{zh} {c['name_en']}".strip()
            out.append(f"- [{label}]({SITE}#{sid})　來源：{vids.get(c['video'], c['video'])} {c['t']}")
        out.append("")

    out += ["## 預計排程", "",
            f"每週一台北時間 09:00 由雲端排程新增 {per_week} 種，依候選清單順序。"
            "實際內容以當週的 PR 為準（不適合的候選會被跳過、由下一個補上）。", ""]
    if not pending:
        out.append("候選清單已經清空。")
    else:
        start = next_monday(max(by_day)) if by_day else next_monday(datetime.date.today().isoformat())
        day = datetime.date.fromisoformat(start)
        for w in range(weeks):
            chunk = pending[w * per_week:(w + 1) * per_week]
            if not chunk:
                break
            out.append(f"- {day.isoformat()}：" + "、".join(c["name_en"] for c in chunk))
            day += datetime.timedelta(days=7)
        rest = len(pending) - per_week * weeks
        if rest > 0:
            out.append(f"- 之後還有 {rest} 種，完整清單：`python3 scripts/candidates.py list --status pending`")
    out.append("")
    return "\n".join(out)


def add_candidates(data, video_id, chapters, existing_keys=()):
    """把章節加進清單；已收錄的風格、已在清單裡的、非風格章節都略過。回傳新加入的項目。"""
    known = set(existing_keys) | {style_key(c["name_en"]) for c in data["candidates"]}
    known |= {c["style_id"] for c in data["candidates"] if c.get("style_id")}
    added = []
    for t, name in chapters:
        k = style_key(name)
        if not is_chapter_style(name) or k in known:
            continue
        c = {"name_en": name.strip(), "video": video_id, "t": t, "status": "pending"}
        data["candidates"].append(c)
        added.append(c)
        known.add(k)
    return added


def check(data, style_ids):
    errs = []
    vids = {v["id"] for v in data.get("videos", [])}
    seen = {}
    for c in data["candidates"]:
        name = c.get("name_en", "?")
        if c.get("status") not in STATUSES:
            errs.append(f"{name}：status 不正確（{c.get('status')}）")
        if c.get("video") not in vids:
            errs.append(f"{name}：影片 {c.get('video')} 不在 videos 清單裡")
        k = style_key(name)
        if k in seen:
            errs.append(f"{name}：和 {seen[k]} 重複")
        seen[k] = name
        if c.get("status") == "done" and c.get("style_id") not in style_ids:
            errs.append(f"{name}：標成 done，但找不到 styles/{c.get('style_id')}.json")
        if c.get("status") == "pending" and (k in style_ids or c.get("style_id") in style_ids):
            errs.append(f"{name}：已經有風格檔，狀態應該改成 done")
    return errs


def source_files():
    if not os.path.isdir(SOURCES):
        return []
    return [os.path.join(SOURCES, n) for n in sorted(os.listdir(SOURCES)) if n.endswith(".json")]


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def style_ids():
    return {n[:-5] for n in os.listdir(STYLES) if n.endswith(".json") and not n.startswith("_")}


def style_keys():
    keys = set(style_ids())
    for n in style_ids():
        keys.add(style_key(load(os.path.join(STYLES, n + ".json")).get("name_en", n)))
    return keys
