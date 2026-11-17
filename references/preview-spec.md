# 示範封面規格（styles/previews/<id>.html）

每種風格都要有一張示範封面。它有兩個用途：風格目錄網頁拿它當預覽圖（使用者可以即時切換配色），做簡報時也拿它當「這個風格做對了的樣子」來參考。所以它必須是這個風格最典型、最有辨識度的一頁。

## 檔案格式

- 一個獨立的 HTML 檔：`<!doctype html>`、`<meta charset="utf-8">`、`<title>`，載入該風格 JSON 裡的 `typography.google_fonts` 連結。
- `<body>` 裡只有一個 `<main class="slide">`，固定 1920×1080 px。
- 不能引用外部圖片。所有圖形用 CSS 或內嵌 SVG 畫。圖片一律用版位（見下方）。
- 檔案大小控制在 40 KB 以內。
- 除了下方的固定腳本，不放其他 JavaScript。

## 顏色只能用這五個變數

```css
:root {
  --bg: <該風格第一組配色 pairs_with 的第一個背景>;
  --ink: <第一組配色的 ink>;
  --a1: <accents[0]>; --a2: <accents[1]，沒有就等於 --a1>; --a3: <accents[2]，沒有就等於 --a2>;
}
```

網頁會用網址參數換掉這些變數，所以畫面上**所有顏色**都必須來自這五個變數（可以用 `color-mix()` 或透明度調淡，但不能寫死其他色碼）。

文字顏色的規則，是為了讓任何一組配色切換後都看得清楚：

- 文字只能用 `--ink`，或在 `--ink` 色塊上用 `--bg`。
- `--a1`～`--a3` 只用在圖形：色塊、線條、記號、圖案、裝飾大字以外的非文字元素。重點色上面不放小字。

## 固定內容（所有風格都一樣，方便比較）

- 小標：2026 品牌提案
- 主標：把想法做成產品
- 英文副標：From Idea to Product
- 資訊：[講者姓名]　2026.11
- 頁碼：01
- 至少一個圖片版位

可以依風格調整呈現方式（例如 Receiptify 把資訊排成收據品項、ASCII 用 `> ` 開頭），但不能改掉文字內容。

## 字體

用該風格 JSON 指定的字體。西文字型在前、中文字型在後，例如 `font-family: "Archivo", "Noto Sans TC", sans-serif;`，即使那段文字是中文也一樣，不然混在裡面的英文和數字會用中文字型的西文字形。

## 圖片版位

照該風格 JSON 的 `placeholder` 描述畫出來，元素加上 `class="ph"`、`data-slot="cover-photo"`、`data-ratio="4/5"`（比例依版面），裡面寫版位說明文字。

## 固定腳本（原樣放在 `</body>` 前）

```html
<script>
(function () {
  var p = new URLSearchParams(location.search);
  ['bg', 'ink', 'a1', 'a2', 'a3'].forEach(function (k) {
    var v = p.get(k);
    if (v && /^[0-9a-fA-F]{6}$/.test(v)) document.documentElement.style.setProperty('--' + k, '#' + v);
  });
  function fit() {
    var s = Math.min(innerWidth / 1920, innerHeight / 1080);
    document.querySelector('.slide').style.transform = 'scale(' + s + ')';
  }
  addEventListener('resize', fit); fit();
})();
</script>
```

並且固定這段基本 CSS：

```css
html, body { margin: 0; height: 100%; overflow: hidden; background: var(--bg); }
.slide { width: 1920px; height: 1080px; transform-origin: 0 0; position: relative; overflow: hidden; background: var(--bg); color: var(--ink); }
```

## 品質要求

- 必須用上 JSON 的 `layout`、`motifs`、`traits`，一眼就能認出是哪個風格。只換字體和顏色不算。
- 不能出現 JSON 的 `avoid` 項目，也要遵守 `references/anti-ai.md`。
- 字級：主標夠大，最小的字也不要小於 20px。
- 不要出現表情符號。
