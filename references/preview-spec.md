# 示範封面規格（styles/previews/<id>.html）

每種風格都要有一張示範封面，給 skill 做簡報時當「這個風格做對了的樣子」來參考。它不放上風格目錄網頁（網頁的參考圖用 Pinterest 嵌入），所以目標只有一個：做成這個風格裡好看、可信的一頁。

## 檔案格式

- 一個獨立的 HTML 檔：`<!doctype html>`、`<meta charset="utf-8">`、`<title>`，載入該風格 JSON 裡的 `typography.google_fonts` 連結。
- `<body>` 裡只有一個 `<main class="slide">`，固定 1920×1080 px。
- 不引用外部圖片，圖片一律用版位（見下方）。
- 檔案大小控制在 40 KB 以內。
- 除了下方的固定腳本，不放其他 JavaScript。

## 好看靠什麼

CSS 擅長的是字體、網格、紙張質感與構圖，不擅長畫寫實插圖。用程式碼畫船錨、仙人掌、公仔，結果多半像廉價美工圖案。所以：

- **主角是字。** 字體、字級對比、字距、行距、對齊方式決定八成的風格感。
- **網格與構圖要有立場。** 照風格 JSON 的 `layout` 決定對齊、留白和破格的位置。
- **質感用材料做。** 紙張纖維、網點、顆粒、影印痕跡、細線、印刷錯位，用 SVG 濾鏡（`feTurbulence`）、漸層、`mix-blend-mode` 做出來。
- **圖形只畫簡單、幾何、符號性的東西。** 例如星芒、齒孔、條碼、框線、幾何模組、徽章外框。需要寫實圖像的地方，一律放圖片版位。

## 配色

在 `:root` 定義 `--bg`、`--ink`、`--a1`～`--a3`，用該風格第一組配色和它的第一個搭配背景。為了好看，可以再定義衍生色（紙張陰影、深淺版本、半透明疊色），寫在 `:root` 裡並註明是從哪個顏色調出來的。文字對背景的對比仍要達到 4.5:1。

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
