#!/usr/bin/env python3
"""列出所有風格，給使用者挑選。

用法：
  python3 scripts/list_styles.py          文字清單
  python3 scripts/list_styles.py --json   機器可讀的摘要
  python3 scripts/list_styles.py <id>     單一風格的背景與配色
"""
import json, os, sys

STYLES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "styles")


def load():
    out = []
    for name in sorted(os.listdir(STYLES)):
        if name.endswith(".json") and not name.startswith("_"):
            with open(os.path.join(STYLES, name), encoding="utf-8") as f:
                out.append(json.load(f))
    return out


def detail(s):
    print(f"{s['name_zh']} {s['name_en']}（{s['id']}）")
    print(f"  {s['summary']}")
    print(f"  重點色上限：{s['color_rules']['max_accents']} 個。{s['color_rules']['notes']}")
    print("  背景：")
    for b in s["backgrounds"]:
        print(f"    {b['id']:<12} {b['name']} {b['hex']}")
    print("  配色：")
    for p in s["palettes"]:
        print(f"    {p['id']:<4} {p['name']}｜文字 {p['ink']}｜重點 {'、'.join(p['accents'])}｜搭配背景 {', '.join(p['pairs_with'])}")
    t = s["typography"]
    print(f"  字體：{t['display']['family']}＋{t['body']['family']}／中文 {t['zh']['family']}")


def main():
    styles = load()
    args = sys.argv[1:]
    if args and args[0] == "--json":
        print(json.dumps([{k: s[k] for k in ("id", "name_zh", "name_en", "summary", "keywords", "best_for", "not_for")}
                          | {"max_accents": s["color_rules"]["max_accents"]} for s in styles], ensure_ascii=False, indent=2))
        return
    if args:
        match = [s for s in styles if s["id"] == args[0]]
        if not match:
            sys.exit(f"找不到風格 {args[0]}，可用的 id：{', '.join(s['id'] for s in styles)}")
        detail(match[0])
        return
    print(f"共 {len(styles)} 種風格\n")
    for n, s in enumerate(styles, 1):
        print(f"{n:>2}. {s['name_zh']} {s['name_en']}（{s['id']}）")
        print(f"    {s['summary']}")
        print(f"    適合：{'、'.join(s['best_for'])}｜不適合：{'、'.join(s['not_for'])}")


if __name__ == "__main__":
    main()
