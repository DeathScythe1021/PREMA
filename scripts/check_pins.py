#!/usr/bin/env python3
"""檢查每個風格的 Pinterest pin 是否還讀得到（網站用的是同一個 Pinterest 公開介面）。

用法：
  python3 scripts/check_pins.py            列出讀不到的 pin，有的話結束碼為 1
  python3 scripts/check_pins.py --fix      直接從風格檔移除讀不到的 pin
  python3 scripts/check_pins.py bauhaus    只檢查指定的風格

讀不到的 pin 在網站上不會顯示；如果剛好是第一張，卡片就沒有封面。
需要網路；連不上 Pinterest 時結束碼為 2，不會改任何檔案。
"""
import json, os, sys, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
STYLES = os.path.join(ROOT, "styles")
API = "https://widgets.pinterest.com/v3/pidgets/pins/info/?pin_ids="


def alive(ids):
    ok = set()
    for k in range(0, len(ids), 10):
        req = urllib.request.Request(API + ",".join(ids[k:k + 10]), headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            for x in json.loads(r.read().decode("utf-8")).get("data") or []:
                if x and x.get("images"):
                    ok.add(str(x["id"]))
    return ok


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    fix = "--fix" in sys.argv
    files = sorted(n for n in os.listdir(STYLES) if n.endswith(".json") and not n.startswith("_"))
    if args:
        files = [f"{a}.json" for a in args]
    styles = {}
    for n in files:
        with open(os.path.join(STYLES, n), encoding="utf-8") as f:
            styles[n] = json.load(f)
    ids = [p["id"] for s in styles.values() for p in s.get("pins", [])]
    try:
        ok = alive(ids)
    except OSError as e:
        print(f"連不上 Pinterest：{e}")
        sys.exit(2)
    bad = 0
    for n, s in styles.items():
        dead = [p for p in s.get("pins", []) if p["id"] not in ok]
        if not dead:
            continue
        bad += len(dead)
        print(f"{s['id']}：{len(dead)} 張讀不到 " + "、".join(p["id"] for p in dead))
        if fix:
            s["pins"] = [p for p in s["pins"] if p["id"] in ok]
            with open(os.path.join(STYLES, n), "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(s, ensure_ascii=False, indent=2) + "\n")
    print(f"共 {len(ids)} 張，讀不到 {bad} 張" + ("，已移除" if fix and bad else ""))
    sys.exit(1 if bad and not fix else 0)


if __name__ == "__main__":
    main()
