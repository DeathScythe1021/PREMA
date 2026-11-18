"""候選風格清單（sources/*.json）的共用函式。CLI 在 scripts/candidates.py。

清單格式：
{
  "channel": {...},
  "videos":     [{"id": "YouTube 影片 ID", "title": "...", "published": "YYYY-MM-DD"}],
  "candidates": [{"name_en": "...", "video": "影片 ID", "t": "1:15",
                  "status": "pending|done|skipped", "style_id": "...", "note": "..."}]
}
"""
import json, os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SOURCES = os.path.join(ROOT, "sources")
STYLES = os.path.join(ROOT, "styles")
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


def mark(data, name, status, style_id=None, note=None):
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
    if note:
        c["note"] = note
    return c


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
