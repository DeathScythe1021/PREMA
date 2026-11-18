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
            "placeholder", "avoid", "color_rules", "backgrounds", "palettes", "prompt_en", "pinterest_queries", "categories"]


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
        warns.append("沒有示範封面（新風格不做圖，做簡報時直接依 JSON 規格）")
    if not s["typography"].get("google_fonts", "").startswith("https://fonts.googleapis.com/css2?"):
        errs.append("typography.google_fonts 必須是 Google Fonts css2 連結")
    max_acc = s["color_rules"].get("max_accents")
    if not isinstance(max_acc, int) or not 1 <= max_acc <= 4:
        errs.append("color_rules.max_accents 必須是 1–4 的整數")
    bgs = {b["id"]: b["hex"] for b in s["backgrounds"]}
    if len(bgs) != 4:
        warns.append(f"背景色建議 4 個，目前 {len(bgs)} 個")
    cats = s.get("categories", [])
    if not (isinstance(cats, list) and 1 <= len(cats) <= 3 and all(isinstance(c, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 &'-]{0,23}", c) for c in cats)):
        errs.append("categories 必須是 1–3 個英文分類（例如 [\"Retro\", \"Typographic\"]）")
    pins = s.get("pins", [])
    for p in pins:
        if not re.fullmatch(r"\d{6,25}", str(p.get("id", ""))):
            errs.append(f"pins 裡的 id 必須是 Pinterest 的數字 ID：{p.get('id')}")
    if len(pins) < 6:
        warns.append(f"Pinterest 參考圖建議 6 張，目前 {len(pins)} 張")
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
    import queue_lib  # noqa: E402
    for path in queue_lib.source_files():
        errs = queue_lib.check(queue_lib.load(path), set(ids))
        print(f"[{'OK ' if not errs else 'ERR'}] sources/{os.path.basename(path)}")
        for e in errs:
            print(f"    錯誤：{e}")
        total_err += len(errs)
        if os.path.basename(path) == "kittl.json":
            names = {s["id"]: s.get("name_zh", "") for _, s in styles}
            cur = ""
            if os.path.exists(queue_lib.UPDATES):
                with open(queue_lib.UPDATES, encoding="utf-8") as f:
                    cur = f.read()
            if queue_lib.render_log(queue_lib.load(path), names) != cur:
                print("[ERR] UPDATES.md\n    錯誤：不是最新的，請執行 python3 scripts/candidates.py log")
                total_err += 1
    print(f"\n共 {len(styles)} 種風格，{total_err} 個錯誤")
    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
