#!/usr/bin/env python3
"""候選風格清單：記錄來源影片裡還沒做成風格檔的風格名稱。

用法（預設清單是 sources/kittl.json，用 --file 指定其他清單）：
  python3 scripts/candidates.py list [--status pending|done|skipped]
  python3 scripts/candidates.py next 3            接下來要做的 3 種
  python3 scripts/candidates.py done "Romantasy" romantasy
  python3 scripts/candidates.py skip "Kidcore" "跳過原因"
  python3 scripts/candidates.py scan              看頻道 RSS 有沒有新的風格影片（只列出、不寫入）
  python3 scripts/candidates.py add-video <影片ID> [--only "名稱" ...]
                                                  把影片章節加進清單（--only 只加指定的章節）
  python3 scripts/candidates.py check             檢查清單和 styles/ 是否一致
"""
import argparse, json, os, re, sys, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import queue_lib as q  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def video_info(vid):
    h = fetch(f"https://www.youtube.com/watch?v={vid}")
    m = re.search(r"ytInitialPlayerResponse\s*=\s*(\{.*?\});\s*(?:var|</script>)", h, re.S)
    if not m:
        raise RuntimeError(f"讀不到影片 {vid} 的資料")
    d = json.loads(m.group(1))
    v = d["videoDetails"]
    pub = d.get("microformat", {}).get("playerMicroformatRenderer", {}).get("publishDate", "")
    return {"id": vid, "title": v["title"], "published": pub[:10]}, v.get("shortDescription", "")


def cmd_list(data, a):
    for c in data["candidates"]:
        if a.status and c["status"] != a.status:
            continue
        extra = c.get("style_id") or c.get("note") or ""
        print(f"[{c['status']:<7}] {c['name_en']:<28} {c['video']} {c['t']:>8}  {extra}")


def cmd_next(data, a):
    vids = {v["id"]: v for v in data["videos"]}
    out = []
    for c in q.next_pending(data, a.n):
        v = vids.get(c["video"], {})
        out.append({**c, "video_title": v.get("title"), "video_url":
                    f"https://www.youtube.com/watch?v={c['video']}&t={_secs(c['t'])}s",
                    "suggested_id": q.style_key(c["name_en"])})
    print(json.dumps(out, ensure_ascii=False, indent=2))


def _secs(t):
    s = 0
    for p in t.split(":"):
        s = s * 60 + int(p)
    return s


def cmd_scan(data, a):
    ch = data["channel"]
    xml = fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['channel_id']}")
    known = {v["id"] for v in data["videos"]} | set(data.get("ignored_videos", []))
    found = []
    for e in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        vid = re.search(r"<yt:videoId>(.*?)<", e).group(1)
        title = re.search(r"<title>(.*?)</title>", e).group(1)
        if vid in known or not q.is_style_video(title):
            continue
        desc = re.search(r"<media:description>(.*?)</media:description>", e, re.S)
        chapters = q.parse_timestamps(desc.group(1) if desc else "")
        found.append({"id": vid, "title": title, "chapters": [f"{t} {n}" for t, n in chapters]})
    print(json.dumps(found, ensure_ascii=False, indent=2))
    if not found:
        print("沒有新的風格影片", file=sys.stderr)
    return False


def cmd_add_video(data, a):
    info, desc = video_info(a.video)
    if not any(v["id"] == a.video for v in data["videos"]):
        data["videos"].append(info)
    chapters = q.parse_timestamps(desc)
    if a.only:
        want = {q.style_key(n) for n in a.only}
        chapters = [(t, n) for t, n in chapters if q.style_key(n) in want]
    added = q.add_candidates(data, a.video, chapters, existing_keys=q.style_keys())
    print(f"{info['title']}：新增 {len(added)} 個候選")
    for c in added:
        print(f"  + {c['name_en']}")
    return True


def cmd_done(data, a):
    q.mark(data, a.name, "done", style_id=a.style_id)
    return True


def cmd_skip(data, a):
    q.mark(data, a.name, "skipped", note=a.note)
    return True


def cmd_check(data, a):
    errs = q.check(data, q.style_ids())
    for e in errs:
        print("錯誤：" + e)
    n = {s: sum(c["status"] == s for c in data["candidates"]) for s in q.STATUSES}
    print(f"待做 {n['pending']}、已做 {n['done']}、跳過 {n['skipped']}，{len(errs)} 個錯誤")
    if errs:
        sys.exit(1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", default=os.path.join(q.SOURCES, "kittl.json"))
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list"); s.add_argument("--status", choices=q.STATUSES); s.set_defaults(f=cmd_list)
    s = sub.add_parser("next"); s.add_argument("n", type=int, nargs="?", default=3); s.set_defaults(f=cmd_next)
    s = sub.add_parser("done"); s.add_argument("name"); s.add_argument("style_id"); s.set_defaults(f=cmd_done)
    s = sub.add_parser("skip"); s.add_argument("name"); s.add_argument("note"); s.set_defaults(f=cmd_skip)
    s = sub.add_parser("scan"); s.set_defaults(f=cmd_scan)
    s = sub.add_parser("add-video"); s.add_argument("video"); s.add_argument("--only", nargs="+"); s.set_defaults(f=cmd_add_video)
    s = sub.add_parser("check"); s.set_defaults(f=cmd_check)
    a = p.parse_args()
    data = q.load(a.file)
    try:
        changed = a.f(data, a)
    except (KeyError, ValueError) as e:
        print(f"錯誤：{e.args[0]}")
        sys.exit(1)
    if changed:
        q.save(a.file, data)


if __name__ == "__main__":
    main()
