# HTML 簡報寫法規範

## 資料夾結構

```
<主題>-deck/
├── index.html     從 assets/deck-shell.html 複製
└── assets/        使用者提供的圖片
```

用瀏覽器打開 `index.html` 就能播放，不需要伺服器。

## 外殼的三個區塊

`deck-shell.html` 的 `<style>` 分成三段：

1. **配色**：把 `--bg`、`--ink`、`--a1`～`--a3` 換成選定的顏色。重點色不足三個時，讓多出來的變數等於最後一個。
2. **簡報引擎**：負責縮放、翻頁、列印。不要修改。
3. **風格**：你要寫的部分。以示範封面 `styles/previews/<id>.html` 的 CSS 為起點，擴充成內頁需要的元件。

也要把 `<link>` 的 `{{GOOGLE_FONTS_URL}}` 換成風格 JSON 的 `typography.google_fonts`，`<title>` 換成簡報標題。

## 投影片

- 每頁一個 `<section class="slide" data-title="頁名">`，畫布固定 1920×1080 px。用 px 排版，引擎會自動縮放。
- 用 class 寫樣式，不要在每頁重複寫一大段 inline style。同一類頁面（章節頁、內容頁、圖片頁）共用同一組 class，讓標題、頁碼的位置固定。
- 頁碼、頁眉這類每頁都有的元素，寫成同一段 HTML，放在每頁相同的位置。
- 講者備註放在 `<aside class="notes">`，不會顯示也不會列印。
- 顏色一律用 CSS 變數，不要在風格區塊寫死色碼。這樣使用者之後想換配色，只要改 `:root`。
- 「色塊專用」的重點色（`check_palette.py` 標示對背景不足 3:1 的）不能拿來寫字或畫細線，只能當面積夠大的色塊；色塊上的字用腳本建議的顏色。

- 很多風格有一個每頁都會出現的「外框」（收據、書頁、登機證、筆記本、卡帶標籤）。動手前先規劃內頁版本：外框的哪些部分每頁都有（頁首、頁尾、條碼），哪些只出現在封面與結尾；扣掉固定部分後，內容區還剩多少高度。內容放不下就拆頁，不要壓縮字級或讓外框超出畫面。
- 每頁重複出現的複雜 SVG（條碼、徽章、齒孔、紋樣）在 `<body>` 開頭用 `<svg style="display:none"><symbol id="barcode">…</symbol></svg>` 定義一次，各頁用 `<svg><use href="#barcode"/></svg>` 引用。
- 示範封面裡為了「任何配色都看得清楚」而寫的技巧（例如深色背景也看得到的雙層疊印），做內頁時只需要照選定的配色處理：淺色背景用單層就夠，不必照搬。
- 示範封面裡直排、旋轉、出血的元素，換到內頁時要避開頁眉與頁碼那一列，長度變了就重新確認不會撞到。
- 示範封面若用了 `oklch(from var(--ink) …)` 這類相對色彩語法，舊瀏覽器可能不支援。在同一個屬性前面先寫一行用 `color-mix()` 或變數的備用值。

## 字級

1920 寬的畫布上的預設建議：主標 96–200px、副標 48–64px、內文 28–36px、說明 20–24px。風格有自己的比例時（例如 Receiptify 的收據字比較小、Blurry Motion 的資訊字刻意很小），以示範封面為準。不管哪種風格，最小都不要低於 20px，整份簡報最多五種字級。

需要固定欄寬的地方（收據欄位、表格、時間軸）用 px，不要用 em：表頭和內容的字級不同時，em 會讓欄位對不齊。

## 圖片版位

需要圖片的地方，先放版位：

```html
<div class="ph ph-portrait" data-slot="s03-team-photo" data-ratio="4/5">
  <span>團隊合照｜4:5</span>
</div>
```

尺寸寫在風格區塊的 class 裡（例如 `.ph-portrait { width: 640px; aspect-ratio: 4/5; }`），不要寫 inline style。外殼給 `.ph` 的 flex 置中只是預設，風格需要時可以覆寫 `display`、`position`（例如用絕對定位疊網點）。不管怎麼畫，版位上都要看得到「內容說明＋比例」這行字，放在版位中央或左下角。

- `data-slot`：版位名稱，用「頁碼＋內容」命名，例如 `s03-team-photo`，方便使用者對照要給哪張圖。
- `data-ratio`：建議比例。
- 版位外觀依風格 JSON 的 `placeholder` 描述來畫，要看得出是這個風格的一部分。`imagery` 允許其他擺法時（例如照片釘在收據旁、貼在筆記本上），可以換位置，但外觀要沿用同一套語言。
- 簡報完成時，列出所有版位：頁碼、`data-slot`、建議內容、比例。

使用者給圖之後：

1. 把圖片複製到 `assets/`，檔名用 `data-slot` 的名稱（例如 `assets/s03-team-photo.jpg`）。
2. 把版位內容換成 `<img class="photo" src="assets/s03-team-photo.jpg" alt="具體描述圖片內容">`，保留外框的尺寸與風格處理。
3. 依風格的 `imagery` 規則處理：例如 Blurry Motion 可以加 `filter: blur()`、Swiss Punk 可以疊一塊 `mix-blend-mode: multiply` 的色塊、Receiptify 轉成單色高對比。
4. 圖片比例和版位不同時，告訴使用者會怎麼裁切，或建議調整版位。

## 檢查畫面

本機有 Google Chrome 時，可以用無頭模式逐頁截圖檢查（網址加 `#頁碼`）。`--user-data-dir` 指向一個這次專用的暫存資料夾，同時有其他截圖在跑時才不會互相干擾。路徑有空格（例如 `Application Support`）時，先轉成正確的檔案網址：`python3 -c "import pathlib,sys;print(pathlib.Path(sys.argv[1]).resolve().as_uri())" index.html`。

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars \
  --user-data-dir=/tmp/deck-shot-profile --window-size=1920,1080 --virtual-time-budget=5000 \
  --screenshot=/tmp/slide-03.png "file:///path/to/index.html#3"
```

匯出 PDF：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --no-pdf-header-footer --virtual-time-budget=8000 \
  --print-to-pdf=/path/to/deck.pdf "file:///path/to/index.html"
```

截圖要看：文字有沒有溢出或被切到、字有沒有疊在一起、版位與圖形是否對齊、每頁標題位置是否一致。
