#!/usr/bin/env python3
"""檢查一組配色的對比度與顏色數量。

用法：
  python3 scripts/check_palette.py --bg "#EFE6D2" --ink "#1F2A44" --accents "#C8352B,#2C5BA8" [--style postage]

規則：
  文字色對背景 >= 4.5:1（內文可讀）
  重點色對背景 >= 3:1（大字、色塊、圖形可辨識）
  指定 --style 時，另外檢查重點色數量是否超過該風格的 max_accents
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STYLES = os.path.join(HERE, "..", "styles")


def parse_hex(h):
    h = h.strip().lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(f"不是六位數 hex 色碼：#{h}")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def luminance(h):
    def ch(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in parse_hex(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def accent_role(bg, ink, a):
    """判斷重點色能怎麼用。

    mark：對背景 >= 3:1，可以當大字、線條、記號。
    fill：對背景不夠，只能當色塊；色塊上要放文字色或背景色的字，且 >= 4.5:1。
    None：兩者都不行，這個顏色在這個背景上不能用。
    """
    if contrast(a, bg) >= 3.0:
        return "mark"
    if max(contrast(ink, a), contrast(bg, a)) >= 4.5:
        return "fill"
    return None


def check(bg, ink, accents, max_accents=None):
    """回傳 (是否全部通過, 訊息列表)。"""
    ok, lines = True, []
    r = contrast(ink, bg)
    passed = r >= 4.5
    ok &= passed
    lines.append(f"{'通過' if passed else '不足'}  文字 {ink} 對背景 {bg}：{r:.2f}:1（需 4.5）")
    for a in accents:
        role = accent_role(bg, ink, a)
        r = contrast(a, bg)
        if role == "mark":
            lines.append(f"通過  重點色 {a}：對背景 {r:.2f}:1，可當大字、線條與記號")
        elif role == "fill":
            on = ink if contrast(ink, a) >= contrast(bg, a) else bg
            lines.append(f"通過  重點色 {a}：對背景只有 {r:.2f}:1，只能當色塊，色塊上的字用 {on}"
                         f"（{contrast(on, a):.2f}:1）")
        else:
            ok = False
            lines.append(f"不足  重點色 {a}：對背景 {r:.2f}:1，當色塊時上面的字也不夠清楚，請換色")
    if max_accents is not None and len(accents) > max_accents:
        ok = False
        lines.append(f"超量  重點色有 {len(accents)} 個，這個風格最多 {max_accents} 個")
    return ok, lines


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bg", required=True)
    p.add_argument("--ink", required=True)
    p.add_argument("--accents", default="")
    p.add_argument("--style", help="風格 id，用來檢查顏色數量上限")
    a = p.parse_args()
    accents = [x.strip() for x in a.accents.split(",") if x.strip()]
    max_acc = None
    if a.style:
        with open(os.path.join(STYLES, a.style + ".json"), encoding="utf-8") as f:
            max_acc = json.load(f)["color_rules"]["max_accents"]
    ok, lines = check(a.bg, a.ink, accents, max_acc)
    print("\n".join(lines))
    print("結果：全部通過" if ok else "結果：有項目未通過，請調整")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
