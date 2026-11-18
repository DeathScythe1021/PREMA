# 自動新增風格的流程

每週的雲端排程，或有人說「從候選清單做幾種新風格」，都照這份做。每種新風格只有一個 `styles/<id>.json`：文字規格加上 Pinterest 參考圖連結。目標是開出一個待審的 PR，讓維護者看過再合併；不要直接 push 到 `main`。

## 資料在哪裡

- `sources/kittl.json`：候選清單。`videos` 是看過的來源影片，`candidates` 是影片章節裡的風格名稱，狀態有 `pending`（待做）、`done`（已做成 `styles/<style_id>.json`）、`skipped`（不做，`note` 寫原因）。
- `ignored_videos`：看過、但內容不是風格清單的影片 ID，之後 scan 不會再列出來。
- `scripts/candidates.py`：管理清單的工具，用法寫在檔案開頭。
- `styles/`：正式風格。`scripts/validate_styles.py` 會一起檢查候選清單和風格檔有沒有對上。

## 步驟

### 1. 開分支、看有沒有新影片

```bash
git checkout -b claude/styles-$(date +%F)
python3 scripts/candidates.py scan
```

`scan` 會列出頻道 RSS 裡還沒看過、標題像風格清單的影片和它的章節。逐支判斷：

- 章節是一個個風格名稱 → `python3 scripts/candidates.py add-video <影片ID>`，加完用 `list --status pending` 看一下，不是風格的章節用 `skip` 標掉。
- 只有部分章節是風格 → `add-video <影片ID> --only "名稱一" "名稱二"`。
- 整支影片只講一種風格 → `add-video <影片ID> --only "<章節名>"`，或先 `add-video` 再把多餘章節 `skip`。
- 不是風格影片 → 把影片 ID 加進 `ignored_videos`。

`scan` 讀不到網路時跳過這步，繼續做清單裡既有的候選。

### 2. 取候選

```bash
python3 scripts/candidates.py next 3
```

照輸出的順序做。做之前先判斷它是不是一個「看得出來、能照著做」的視覺風格：只是社群版面格式、只是一種技法、或跟現有風格幾乎一樣的，用 `skip` 標掉並寫原因，然後往下取一個補上。

### 3. 研究風格

- 先看 `video_url`（已經帶到該章節的時間點）的影片標題和說明，再用網路搜尋查這個風格的來源、年代、代表作品和常見元素。不要只憑記憶寫。
- 讀 `styles/_template.json`、`references/anti-ai.md`，再挑兩個現有風格的 JSON 當寫法參考（例如 `googie`、`swiss-punk`）。

### 4. 寫風格檔 `styles/<id>.json`

- `id` 用 `next` 給的 `suggested_id`，必要時再調短。
- `source.title` 寫成 `Kittl — <影片標題>`，`source.url` 用帶時間點的影片網址。
- 中文用台灣用語、全形標點，語氣照現有風格檔：具體、短句，不寫「賦能」「打造」「不只是 A，更是 B」。
- `name_zh` 有通用中文譯名就用；沒有的話取一個好懂的名字。
- 4 個背景、4 組配色，重點色數量不超過 `color_rules.max_accents`。寫完跑 `python3 scripts/check_palette.py` 或直接跑 `validate_styles.py` 確認對比通過。
- 字體只用 Google Fonts，`google_fonts` 連結要包含 display、body 和中文字體。
- `categories` 用網站上已有的分類名稱為主（看其他 JSON 的 `categories`），真的沒有合適的才新增。

### 5. 不做圖

新風格一律不做示範封面（`styles/previews/`）、不截圖、不生成任何圖片。參考圖只用 Pinterest 連結。`validate_styles.py` 對沒有示範封面的風格只會出提醒，不算錯誤。

### 6. Pinterest 參考圖

- 用 `pinterest_queries` 的關鍵字搜尋，搜尋範圍限定在 `pinterest.com` 網域（`site:pinterest.com/pin` 這種寫法搜不到結果），從結果網址 `pinterest.com/pin/<數字>` 取出 pin ID。
- Pinterest 頁面通常抓不到內容，只能依搜尋結果的標題和摘要判斷是否相關；`note` 用英文寫它是什麼。優先選有明確作品名、作者或風格名稱的 pin，少用素材商品頁。
- 同一張作品常有好幾個 pin，標題相同的只留一個。
- 目標 6 張。找不到 6 張就照實際數量填，不要湊數或編造 ID；validate 會出提醒，沒關係。
- 這些 pin 都還沒人看過，PR 說明裡一定要列出來請維護者確認。

### 7. 更新清單、檢查

```bash
python3 scripts/candidates.py done "<name_en>" <id>   # 會記下今天的日期
python3 scripts/candidates.py log                    # 重新產生 UPDATES.md（更新紀錄＋預計排程）
python3 -m unittest discover tests
python3 scripts/validate_styles.py
python3 scripts/build_site.py --out _site
```

全部通過才能開 PR。`validate_styles.py` 也會檢查 `UPDATES.md` 是不是最新的，忘了跑 `log` 會報錯。有錯就修，修不好的風格就把檔案移除、候選改回 `pending`，在 PR 說明裡寫原因。

同時更新 `README.md` 和 `SKILL.md` 裡的風格數量（「目前收錄：N 種風格」「目前 N 種」）。

### 8. 開 PR

commit 訊息：`Add styles: <英文名一>, <英文名二>, <英文名三>`。PR 說明用這個格式：

```markdown
## 這次新增的風格

### <name_zh> <name_en>（`<id>`）
<summary>
- 來源：<影片標題>（<時間點連結>）
- 參考圖（請點開確認，不對的請刪掉或換掉）：
  - [ ] https://www.pinterest.com/pin/<pin id>/ — <note>

## 跳過的候選
- <name_en>：<原因>

## 檢查結果
validate_styles.py：<N> 種風格，0 個錯誤
```

不要合併、不要開 auto-merge，留給維護者審。
