#!/usr/bin/env python3
"""驗證 styles/ 裡每個風格檔的格式、示範封面與配色對比。

用法：python3 scripts/validate_styles.py
GitHub Actions 每次 push 都會執行；有錯誤時結束碼為 1。
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_palette import check  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
STYLES = os.path.join(ROOT, "styles")

REQUIRED = ["id", "name_zh", "name_en", "source", "summary", "definition", "keywords",
            "best_for", "not_for", "traits", "layout", "motifs", "typography", "imagery",
            "placeholder", "avoid", "color_rules", "backgrounds", "palettes"]


def load_styles():
    out = []
    for name in sorted(os.listdir(STYLES)):
        if name.endswith(".json") and not name.startswith("_"):
            with open(os.path.join(STYLES, name), encoding="utf-8") as f:
                out.append((name, json.load(f)))
    return out


def validate(name, s):
    errs, warns = [], []
    for k in REQUIRED:
        if k not in s or s[k] in ("", [], {}):
            errs.append(f"缺少欄位：{k}")
    if errs:
        return errs, warns
    if s["id"] + ".json" != name:
        errs.append(f"檔名必須是 {s['id']}.json")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", s["id"]):
        errs.append("id 只能用小寫英數與連字號")
    if not os.path.exists(os.path.join(STYLES, "previews", s["id"] + ".html")):
        errs.append(f"缺少示範封面 styles/previews/{s['id']}.html")
    if not s["typography"].get("google_fonts", "").startswith("https://fonts.googleapis.com/css2?"):
        errs.append("typography.google_fonts 必須是 Google Fonts css2 連結")
    max_acc = s["color_rules"].get("max_accents")
    if not isinstance(max_acc, int) or not 1 <= max_acc <= 4:
        errs.append("color_rules.max_accents 必須是 1–4 的整數")
    bgs = {b["id"]: b["hex"] for b in s["backgrounds"]}
    if len(bgs) != 4:
        warns.append(f"背景色建議 4 個，目前 {len(bgs)} 個")
    if len(s["palettes"]) != 4:
        warns.append(f"配色建議 4 組，目前 {len(s['palettes'])} 組")
    for p in s["palettes"]:
        if not p.get("pairs_with"):
            errs.append(f"配色 {p['id']} 沒有 pairs_with")
            continue
        for bg_id in p["pairs_with"]:
            if bg_id not in bgs:
                errs.append(f"配色 {p['id']} 指到不存在的背景 {bg_id}")
                continue
            ok, lines = check(bgs[bg_id], p["ink"], p["accents"], max_acc)
            if not ok:
                errs.append(f"配色 {p['id']} 搭 {bg_id}：" + "；".join(l for l in lines if not l.startswith("通過")))
    return errs, warns


def main():
    styles = load_styles()
    ids = [s["id"] for _, s in styles]
    total_err = 0
    if len(ids) != len(set(ids)):
        print("錯誤：有重複的風格 id")
        total_err += 1
    for name, s in styles:
        errs, warns = validate(name, s)
        status = "OK " if not errs else "ERR"
        print(f"[{status}] {name}")
        for e in errs:
            print(f"    錯誤：{e}")
        for w in warns:
            print(f"    提醒：{w}")
        total_err += len(errs)
    print(f"\n共 {len(styles)} 種風格，{total_err} 個錯誤")
    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
