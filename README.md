# ⚙ NDT 派工管理系統

非破壞檢測（NDT）人員派工管理系統，部署於 GitHub Pages，支援 PDF 證照自動解析。

## 功能

| 頁面 | 說明 |
|------|------|
| 📋 派工作業 | 輸入工號、檢測方法、人數，系統自動建議合格人員並支援手動勾選 |
| 📊 工號管理 | 追蹤每個工號的進度，勾選過程管制表/報告/完工狀態 |
| 📈 支援統計 | 以年度為單位統計每位人員各檢測方法的支援次數 |
| 👤 人員證照 | 總覽所有人員的 TPC 證照級數（PT/MT/UT/ET/RT/VT/LT） |

### 派工規則
- 每次派工至少需要一位 **Level II 以上** 人員
- Level II+ 人員帶領 Level I 或無證照人員
- 系統依 Level III → II → I 順序自動建議

## 快速開始

### 1. 建立 GitHub Repository

```bash
git clone https://github.com/<你的帳號>/ndt-dispatch.git
cd ndt-dispatch
```

### 2. 啟用 GitHub Pages

1. 進入 repo → **Settings** → **Pages**
2. Source 選擇 **Deploy from a branch**
3. Branch 選擇 **main** / **(root)**
4. 儲存後等待部署完成

### 3. 啟用 GitHub Actions

1. 進入 repo → **Settings** → **Actions** → **General**
2. 確認 Workflow permissions 設為 **Read and write permissions**
3. 勾選 **Allow GitHub Actions to create and approve pull requests**

## 更新人員證照資料

只需將新的 PDF 檔案放入 `data/` 資料夾並推送：

```bash
# 將新的證照 PDF 複製到 data/ 資料夾
cp 證書級數XXXX.pdf data/

# 推送到 GitHub
git add data/
git commit -m "更新證照資料"
git push
```

GitHub Actions 會自動：
1. 偵測 `data/*.pdf` 檔案變更
2. 執行 Python 腳本解析 PDF 表格
3. 產生 `data/personnel.json`
4. 將資料注入 `index.html`
5. 自動 commit 並推送更新

也可以手動觸發：進入 **Actions** → **Parse Certification PDF** → **Run workflow**

## PDF 格式要求

PDF 必須包含如下表格結構：

| 序號 | 姓名 | 檢測類別 | PT (Ⅰ/Ⅱ/Ⅲ) | MT (Ⅰ/Ⅱ/Ⅲ) | UT | ET | RT | VT | LT |
|------|------|----------|-------------|-------------|----|----|----|----|-----|

- 每位人員佔兩行：**TPC** 行（公司認證）+ **協會證照** 行
- 系統只提取 **TPC** 行的資料
- 序號 2~30 的人員資料會被提取

## 檔案結構

```
ndt-dispatch/
├── index.html                          # 前端主頁面
├── data/
│   ├── personnel.json                  # 自動產生的人員資料
│   └── *.pdf                           # 證照 PDF（觸發自動解析）
├── scripts/
│   ├── parse_cert_pdf.py              # PDF 解析腳本
│   └── update_frontend.py            # 資料注入前端腳本
├── .github/
│   └── workflows/
│       └── parse-cert.yml             # GitHub Actions 工作流程
├── requirements.txt
└── README.md
```

## 資料儲存

- **人員證照資料**：寫入 `index.html` 中的 JavaScript，隨 GitHub Pages 部署
- **派工紀錄**：儲存於瀏覽器 `localStorage`，僅限同一瀏覽器存取

> ⚠️ 注意：派工紀錄存在 localStorage 中，清除瀏覽器資料會遺失紀錄。如需跨裝置同步，未來可擴充後端資料庫。

## 技術

- 前端：純 HTML/CSS/JS（無框架依賴）
- PDF 解析：Python + pdfplumber
- CI/CD：GitHub Actions
- 部署：GitHub Pages
