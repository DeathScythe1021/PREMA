# PREMA

PREMA 是一個設計風格靈感庫，收錄定義明確的美術風格。每種風格都有 Pinterest 參考圖、英文 prompt、背景色和配色，可以拿來找靈感、跟團隊確認方向，或交給 AI 生成工具。

這個 repo 同時是一個 Claude skill：選好風格之後，可以請 Claude 照那套規則做出 HTML 簡報。網站和 skill 讀的是同一份風格資料。

- 風格目錄：https://deathscythe1021.github.io/PREMA/
- 目前收錄：44 種風格
- 更新紀錄與預計排程：[UPDATES.md](UPDATES.md)

## 為什麼要先定風格

設計方向模糊的時候，每個地方都會選最保險的做法，結果什麼風格都不像。AI 產出的東西尤其明顯：漸層、圓角卡片、置中排版、表情符號圖示。

所以這裡的每種風格都寫清楚版面規則、字體、招牌圖形、配色上限和禁忌，看圖就分得出來，也能照著做。

## 當作靈感使用

1. 到風格目錄依分類或氣氛篩選，看各風格的參考圖。
2. 在風格頁複製英文 prompt，或記下背景色和配色。
3. 用在你的設計、提案，或貼進 AI 生成工具。

## 用 Claude 做簡報

### 安裝

把這個 repo clone 到 Claude Code 的個人 skills 資料夾：

```bash
git clone https://github.com/DeathScythe1021/PREMA.git ~/.claude/skills/art-style-deck
```

之後在 Claude Code 說「幫我做一份簡報」或「用 Postage 風格做投影片」，Claude 就會啟用這個 skill。

更新風格清單：

```bash
git -C ~/.claude/skills/art-style-deck pull
```

### 使用流程

1. **內容**：告訴 Claude 主題、聽眾、頁數，有現成資料就一起給。
2. **風格**：到風格目錄網頁看各風格的 Pinterest 參考圖和英文 prompt，挑一種；也可以讓 Claude 依內容推薦。
3. **背景**：每種風格有 4 個背景色，也可以讓 Claude 推薦。
4. **配色**：每種風格有 4 組預設配色。要用自己的顏色也可以，但重點色數量不能超過該風格的上限，也要通過對比檢查。
5. **確認**：Claude 會列出設定摘要，確認後才開始做。
6. **放圖**：簡報完成後會列出所有圖片版位，你把圖給 Claude，它會放進去並依風格處理。

在網頁的風格頁選好背景和配色後，按「複製指令」，貼給 Claude 就能直接開始。

## 新增風格

1. 複製 `styles/_template.json` 成 `styles/<風格 id>.json`，填好每個欄位。
2. 示範封面（`styles/previews/<風格 id>.html`）可以不做；新風格一律只寫 JSON 和 Pinterest 參考圖連結。
3. 在 JSON 寫好英文分類（`categories`）、英文 prompt（`prompt_en`）和搜尋關鍵字（`pinterest_queries`），再到 Pinterest 挑 6 張參考圖，把 pin 網址裡的數字 ID 填進 `pins`。
4. 執行檢查：

   ```bash
   python3 scripts/validate_styles.py
   ```

5. commit 並 push 到 `main`，GitHub Actions 會重新檢查並更新網頁。

也可以直接跟 Claude 說「幫我在 art-style-deck 新增一個風格」，它會照上面的步驟做。

## 自動新增風格（每週排程）

新風格的來源以 Kittl YouTube 頻道為主。頻道影片裡提到、還沒收錄的風格名稱記在 `sources/kittl.json`（候選清單），每筆標「待做 pending／已做 done／跳過 skipped」。

每週一早上，Claude 的雲端排程會照 `references/auto-update.md` 做：

1. 檢查 Kittl 頻道有沒有新的風格影片，有的話把新風格加進候選清單。
2. 從候選清單取 3 種，寫風格檔，並找候選 Pinterest 參考圖連結（不做任何圖）。
3. 跑檢查，開一個待審的 PR，附上每張參考圖的連結。

維護者要做的事：

- **審 PR**：點開參考圖連結，不對的 pin 刪掉或換掉，沒問題就合併，網頁會自動更新。
- **不想收某個風格**：`python3 scripts/candidates.py skip "Kidcore" "原因"`，或直接跟 Claude 說「候選清單跳過 Kidcore」。
- **加新的來源影片**：`python3 scripts/candidates.py add-video <YouTube 影片 ID>`。
- **看哪天更新了哪幾種、接下來每週預計做哪幾種**：看 [UPDATES.md](UPDATES.md)，每次排程都會自動更新。
- **看還剩哪些**：`python3 scripts/candidates.py list --status pending`。

候選清單和 `styles/` 對不上（例如標成已做但沒有風格檔）時，`validate_styles.py` 會報錯，GitHub Actions 也會擋下來。

## 部署風格目錄網頁

第一次需要在 GitHub 開啟 Pages：repo 的 **Settings → Pages → Build and deployment → Source** 選 **GitHub Actions**。之後每次 push 到 `main`，網頁都會自動更新。

在本機預覽：

```bash
python3 scripts/build_site.py --out _site
open _site/index.html
```

## 資料夾結構

```
styles/<id>.json            風格規格
styles/previews/<id>.html   示範封面（只有最早的 25 種有；給 Claude 參考，不上網站）
assets/deck-shell.html      HTML 簡報外殼
sources/kittl.json          候選風格清單（來源影片與待做／已做／跳過）
UPDATES.md                  更新紀錄與預計排程（由 scripts/candidates.py log 產生）
references/                 寫給 Claude 的規範（去 AI 感清單、簡報寫法、封面規格、自動新增流程）
scripts/                    列出風格、檢查配色、驗證資料、產生網頁、管理候選清單
tests/                      腳本的單元測試
site/template.html          風格目錄網頁模板
SKILL.md                    skill 本體
```

## 風格來源

目前的風格名稱整理自 Kittl 的兩支影片：

- [10 Cool Design Style Names You've Been Searching For](https://www.youtube.com/watch?v=WHYVUPs8L3k)
- [15 More Design Styles You've Never Heard Of](https://www.youtube.com/watch?v=uZWnxa4mkKA)

網站上的參考圖透過 Pinterest 官方嵌入顯示，圖片沒有下載到這個 repo，版權屬於原作者。

影片只提供風格名稱與參考圖；各風格的定義、配色與示範封面是這個專案另外撰寫的。
