# Project & Token Monitor Dashboard

輕量級自動化靜態網頁 Dashboard，監控 GitHub 專案狀態與 MiniMax Token 消耗。

## 功能特色

- 📊 **專案健康度看板** - GitHub Issues、PRs、Commits 狀態
- 💰 **Token 消耗追蹤** - 趨勢圖、每日消耗、月度預估成本
- 📁 **Context 檔案瀏覽器** - 視覺化目錄樹、Token 佔用分析
- ⚔️ **審計報告** - 競品分析、優化建議、優先行動清單

## 專案結構

```
project-token-monitor/
├── .github/
│   └── workflows/
│       └── collect-data.yml    # GitHub Actions 定時收集數據
├── data/
│   └── dashboard-data.json     # 數據輸出檔案
├── scripts/
│   └── collect_data.py         # Python 數據收集腳本
├── index.html                  # 前端 Dashboard
└── README.md
```

## 快速開始

### 1. 克隆專案

```bash
git clone https://github.com/openclawsean024-create/project-token-monitor.git
cd project-token-monitor
```

### 2. 運行數據收集腳本（本地端）

```bash
pip install requests
python scripts/collect_data.py
```

### 3. 部署到 GitHub Pages

1. 前往 GitHub Repository Settings
2. 選擇 **Pages** 
3. Source 選擇 `main` branch `/ (root)`
4. 儲存後即可訪問

## 自動化

GitHub Actions 會自動每 6 小時執行一次數據收集，並更新 `data/dashboard-data.json`。

### 手動觸發

前往 Actions 頁面，點擊 "Data Collection Pipeline" → "Run workflow"

## Token 計算方式

- **中文**: 1 字元 ≈ 1 Token
- **英文**: 1 字元 ≈ 0.3 Token

## 技術堆疊

- **前端**: TailwindCSS + Chart.js
- **數據收集**: Python
- **部署**: GitHub Pages (Static)
- **自動化**: GitHub Actions

## 預覽

打開 `index.html` 即可本地預覽，或訪問部署後的 GitHub Pages URL。

---

Built with ❤️ for OpenClaw
