# Art Style Deck

一個 Claude skill，加上一個風格目錄網頁。

做簡報時，先從目錄挑一種定義明確的美術風格，再選背景和配色，Claude 會照那套風格的規則做出 HTML 簡報。圖片先留版位，等你給圖再放進去。

- 風格目錄：（部署後填入 GitHub Pages 網址）
- 目前收錄：25 種風格

## 為什麼要先選風格

AI 做的簡報常常看起來差不多：漸層、圓角卡片、置中排版、表情符號圖示。原因是沒有明確的美術方向，每個地方都選了最保險的做法。

這個 skill 的做法是先把方向定死。每種風格都寫清楚它的版面規則、字體、招牌圖形、配色上限和禁忌，Claude 做每一頁時都回到這套規則。

## 安裝

把這個 repo clone 到 Claude Code 的個人 skills 資料夾：

```bash
git clone <這個 repo 的網址> ~/.claude/skills/art-style-deck
```

之後在 Claude Code 說「幫我做一份簡報」或「用 Postage 風格做投影片」，就會用到這個 skill。

更新風格清單：

```bash
git -C ~/.claude/skills/art-style-deck pull
```

## 使用流程

1. **內容**：告訴 Claude 主題、聽眾、頁數，有現成資料就一起給。
2. **風格**：在風格目錄網頁挑一種，或讓 Claude 依內容推薦。
3. **背景**：每種風格有 4 個背景色，也可以讓 Claude 推薦。
4. **配色**：每種風格有 4 組預設配色。要用自己的顏色也可以，但重點色數量不能超過該風格的上限，也要通過對比檢查。
5. **確認**：Claude 會列出設定摘要，確認後才開始做。
6. **放圖**：簡報完成後會列出所有圖片版位，你把圖給 Claude，它會放進去並依風格處理。

在網頁上選好風格、背景和配色後，按「複製指令」，貼給 Claude 就能直接開始。

## 新增風格

1. 複製 `styles/_template.json` 成 `styles/<風格 id>.json`，填好每個欄位。
2. 照 `references/preview-spec.md` 做一張示範封面 `styles/previews/<風格 id>.html`。
3. 執行檢查：

   ```bash
   python3 scripts/validate_styles.py
   ```

4. commit 並 push 到 `main`，GitHub Actions 會重新檢查並更新網頁。

也可以直接跟 Claude 說「幫我在 art-style-deck 新增一個風格」，它會照上面的步驟做。

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
styles/previews/<id>.html   示範封面
assets/deck-shell.html      HTML 簡報外殼
references/                 寫給 Claude 的規範（去 AI 感清單、簡報寫法、封面規格）
scripts/                    列出風格、檢查配色、驗證資料、產生網頁
site/template.html          風格目錄網頁模板
SKILL.md                    skill 本體
```

## 風格來源

目前的風格名稱整理自 Kittl 的兩支影片：

- [10 Cool Design Style Names You've Been Searching For](https://www.youtube.com/watch?v=WHYVUPs8L3k)
- [15 More Design Styles You've Never Heard Of](https://www.youtube.com/watch?v=uZWnxa4mkKA)

各風格的規格與示範封面是另外撰寫的。
