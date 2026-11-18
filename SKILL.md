---
name: art-style-deck
description: 引導使用者先挑一種明確的美術風格（目前 37 種，例如 Swiss Punk、Dark Academia、Wabi Sabi、Receiptify、Postage、Googie、Neo-Brutalism、Blurry Motion、ASCII Art，清單會持續擴充），再挑背景色與配色，最後做出沒有 AI 感的 HTML 簡報；圖片先留版位，等使用者提供再放入。只要使用者想做簡報、投影片、deck、提案、slides、自我介紹簡報、作品集簡報，或說「幫我挑一個風格」「不要 AI 感的簡報」「用某某風格做投影片」，就使用這個 skill，即使沒有明講 HTML 也一樣：這個 skill 的簡報一律輸出成 HTML。
---

# Art Style Deck：先選風格，再做簡報

這個 skill 的目的，是讓簡報有清楚的美術方向，而不是「看起來還行」的 AI 預設樣式。AI 感通常來自「什麼都做一點」：漸層、圓角卡片、置中、表情符號圖示、平均分配的三欄。解法是先選定一種有明確規則的風格，之後每個設計決定都回到那套規則。

所以流程是固定的：**內容 → 風格 → 背景 → 配色 → 確認 → 製作 → 放圖 → 自我檢查**。前四步都要使用者自己選，不要替他決定；你可以推薦，但要說明理由，最後由使用者拍板。

## 檔案地圖

```
art-style-deck/
├── styles/<id>.json         每種風格的規格（定義、版面、字體、配色、禁忌）
├── styles/previews/<id>.html  該風格的示範封面，也是最好的實作參考
├── assets/deck-shell.html   HTML 簡報外殼（縮放、翻頁、列印、圖片版位）
├── references/anti-ai.md    去 AI 感檢查清單
├── references/deck-spec.md  HTML 簡報的寫法規範
├── references/preview-spec.md  新增風格時，示範封面的規格
├── site/template.html       風格目錄網頁模板（scripts/build_site.py 會產生網頁）
├── scripts/list_styles.py   列出所有風格（給使用者選）
├── scripts/check_palette.py 檢查配色對比與顏色數量
└── config.json              風格目錄網頁的網址
```

風格清單會在 GitHub 上持續新增，所以**永遠以 `styles/` 資料夾實際內容為準**，不要憑記憶列風格。skill 資料夾裡有 `.git` 時，開始前先更新：`git -C <skill 資料夾> pull --ff-only`（失敗就略過，用本機版本）。

**使用者已經選好的步驟直接跳過**：使用者貼上風格目錄網頁的指令（「用 art-style-deck 做簡報：風格 postage、背景 envelope、配色 P1」），或在對話裡直接講明風格、背景、配色，那些步驟就不用再問。讀取對應的風格 JSON，確認名稱或 id 對得上，只問還沒決定的部分。

## 步驟 1：了解內容

先問清楚這幾件事，使用者已經給的就不要重問：

- 主題與目的（提案、自我介紹、成果報告、教學……）
- 聽眾是誰、在哪裡播放（會議室投影、線上分享、印出來）；使用者沒說的話，先假設投影播放，寫進步驟 5 的摘要讓他確認
- 大約幾頁、有沒有現成資料（文字稿、舊簡報、PDF）

有現成資料就先讀完，再整理成每頁大綱。風格會影響版面，但內容結構要先站穩。

## 步驟 2：選風格

執行 `python3 scripts/list_styles.py` 取得目前所有風格（id、中英文名、一句話定義、適合／不適合的內容）。

給使用者看兩樣東西：

1. **風格目錄網頁**：`config.json` 的 `gallery_url`。網頁上每種風格都有 Pinterest 參考圖、英文 prompt 和配色，看圖比看文字準確。如果網址還沒設定，就執行 `python3 scripts/build_site.py --out <簡報資料夾>/_gallery`，再用 `open <簡報資料夾>/_gallery/index.html`（macOS）幫使用者打開；不能執行 `open` 時，告訴使用者檔案位置。
2. **文字清單**：每種風格一行，標出你依內容推薦的 2–3 種，並用一句話說明為什麼適合。

風格之間差異很大，不要混搭。使用者說「Googie 加一點 ASCII」的時候，說明混搭會讓兩種風格都失去辨識度，請他選一個主風格；另一種的元素最多只能當單頁的點綴。

## 步驟 3：選背景色

背景會決定整份簡報的氣氛，所以和配色分開選。讀取該風格 JSON 的 `backgrounds`（每種風格 4 個），列給使用者選。

使用者說「你決定」或「自動」時，依內容與播放場所推薦一個，並說明理由。一般來說，會議室、教室投影、要印出來的簡報選淺色；燈光較暗的展演、活動開場、情緒型簡報選深色。使用者已經先指定配色時，只能從那組配色的 `pairs_with` 裡挑背景。

## 步驟 4：選配色

讀取該風格的 `palettes`（每種 4 組）。每組有文字色 `ink` 和重點色 `accents`，以及建議搭配的背景 `pairs_with`。列出時標明哪幾組和步驟 3 選的背景相容。

使用者想用自己的顏色（例如品牌色）可以，但有兩個限制，要明確告訴他原因：

- **顏色數量上限**：重點色不能超過該風格的 `color_rules.max_accents`。每種風格的上限不同（例如 Blurry Motion 只能 1 個，Cassette Core 可以 3 個），因為顏色一多，風格就散了。超過時請他刪減，或建議改用上限較高的風格。
- **對比**：執行 `python3 scripts/check_palette.py --bg <背景> --ink <文字色> --accents <色1,色2> --style <風格 id>`。文字色對背景至少要 4.5:1。重點色分成兩種用法：對背景達 3:1 的可以當大字、線條、記號；不到 3:1 的（例如奶油底上的芥末黃）只能當色塊，色塊上的字用腳本建議的顏色。兩種都不行就提出最接近的可用色，讓使用者決定。

預設的 4 組配色都已經通過這項檢查，直接用不需要再跑；使用者自訂顏色或換背景時才需要。

## 步驟 5：確認設定

動手前，用一段簡短的設定摘要請使用者確認：

```
風格：Postage 郵票設計
背景：信封米 #EFE6D2
配色：P1 航空郵件（文字 #1F2A44／重點 #C8352B、#2C5BA8）
字體：Old Standard TT＋Archivo Narrow／中文 Noto Serif TC
頁數：12 頁（大綱如下）
```

使用者確認後才開始做。改設定很便宜，重做整份簡報很貴。

## 步驟 6：製作 HTML 簡報

1. 讀 `references/deck-spec.md`（外殼怎麼用、版位怎麼寫）和 `references/anti-ai.md`。
2. 讀選定風格的 JSON 全文和 `styles/previews/<id>.html`。示範封面是這個風格「做對了」的樣子，內頁要延續同一套字體、線條、質感與構圖手法。沒有示範封面的風格（後來新增的都沒有），就直接依 JSON 的 `layout`、`motifs`、`traits`、`typography` 做，並參考 Pinterest 參考圖的描述。
3. 複製 `assets/deck-shell.html` 為使用者的簡報檔，例如 `<主題>-deck/index.html`。在 `:root` 填入選定的背景與配色變數，再逐頁寫 `<section class="slide">`。
4. 每頁只講一件事。條列超過 4 點就拆頁，或改成表格、數字、引言。
5. 風格 JSON 的 `layout` 和 `motifs` 要真的用上（例如 Postage 的齒孔邊與郵戳、ASCII 的字元格線），不能只套顏色和字體。只換顏色的簡報，看起來還是 AI 模板。

## 步驟 7：圖片版位

**不要自己生成圖片，也不要找圖庫照片填進去。** 圖片是這個 skill 留給使用者的部分。

- 需要圖的地方，放 `deck-spec.md` 定義的版位元素，寫上這裡適合放什麼圖、比例多少。版位的外觀要符合風格（JSON 的 `placeholder`）。
- 簡報完成後，列出所有版位清單：頁碼、版位名稱、建議內容、比例。
- 使用者給圖之後，把圖片複製到簡報的 `assets/` 資料夾，把版位換成 `<img>`，並照風格的 `imagery` 規則處理（例如 Blurry Motion 加動態模糊、Knolling 維持俯拍不裁斜）。給的圖和版位比例不合時，說明會怎麼裁切。

## 步驟 8：自我檢查與交付

1. 逐條對照 `references/anti-ai.md`，有違反的地方直接修。
2. 簡報裡的繁體中文文字如果有 `speak-human-tw` skill 可用，就用它檢查語感；依那個 skill 的規則，先列建議、等使用者回覆再改。
3. 交付時告訴使用者：檔案位置、怎麼播放（瀏覽器開啟、方向鍵翻頁、F 全螢幕、列印成 PDF）、待補的圖片版位清單，以及哪些數字是推算出來的、哪些句子是你加的，請使用者確認。

## 新增風格

使用者想新增風格時：

1. 複製 `styles/_template.json` 成 `styles/<id>.json`，照格式填寫。定義要具體到「看到畫面就能判斷是不是這個風格」，並和現有風格有明顯差別；太接近的話，改成在現有風格裡多一組配色。
2. 不做示範封面，也不生成任何圖片；參考圖只用 Pinterest 連結。完整流程見 `references/auto-update.md`。
3. 寫 `prompt_en`（5–7 條英文重點，描述這個風格的視覺特徵）和 `pinterest_queries`（2 個搜尋關鍵字），再到 Pinterest 挑 6 張代表性的作品，把 pin 的數字 ID 寫進 `pins`。只存 ID，網站會用 Pinterest 官方嵌入顯示，不下載圖片。
4. 執行 `python3 scripts/validate_styles.py`，它會檢查欄位、pin ID、每組配色的對比和候選清單。
5. 通過後 commit 並 push 到 GitHub（push 前先問使用者），網頁會自動更新。
