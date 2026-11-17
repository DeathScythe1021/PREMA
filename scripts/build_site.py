#!/usr/bin/env python3
"""從 styles/ 產生風格目錄網頁。

用法：python3 scripts/build_site.py --out _site
產出：_site/index.html、_site/styles.json
（示範封面 styles/previews/ 是給 skill 做簡報時參考的，不放上網站；網站的參考圖用 Pinterest 官方嵌入。）
GitHub Actions 會在每次 push 後執行這支腳本，並部署到 GitHub Pages。
"""
import argparse, json, os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
STYLES = os.path.join(ROOT, "styles")
TEMPLATE = os.path.join(ROOT, "site", "template.html")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "_site"))
    out = os.path.abspath(ap.parse_args().out)

    styles = []
    for name in sorted(os.listdir(STYLES)):
        if name.endswith(".json") and not name.startswith("_"):
            with open(os.path.join(STYLES, name), encoding="utf-8") as f:
                styles.append(json.load(f))

    os.makedirs(out, exist_ok=True)

    data = json.dumps(styles, ensure_ascii=False).replace("</", "<\\/")
    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read().replace("__DATA__", data).replace("__COUNT__", str(len(styles)))
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(out, "styles.json"), "w", encoding="utf-8") as f:
        json.dump(styles, f, ensure_ascii=False, indent=2)
    open(os.path.join(out, ".nojekyll"), "w").close()
    print(f"已產生 {len(styles)} 種風格的目錄：{os.path.join(out, 'index.html')}")


if __name__ == "__main__":
    main()
