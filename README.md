# 音訊/影片轉文字系統

這是一個基於 Streamlit 開發的應用程式，可以將音訊或影片檔案轉換成文字逐字稿和字幕檔。系統支援多語言辨識，並可自動翻譯成繁體中文。

## 功能特點

- 支援多種音訊和影片格式（mp3、wma、wav、m4a、mp4、mov、avi、mkv）
- 自動語言辨識和翻譯
- 生成逐字稿（支援編輯和下載）
- 生成字幕檔（SRT 格式）
- 支援雙語字幕輸出
- 使用 OpenAI API 進行智能分段和翻譯
- 直覺的網頁介面

## 系統需求

- Python 3.10 或以上版本
- FFmpeg（如果系統未安裝，程式會自動下載）
- CUDA 支援（可選，用於加速處理）
- OpenAI API 金鑰

## 安裝步驟

1. 克隆專案到本地：
```bash
git clone https://github.com/clinno0616/hello11.git
cd hello11
```

2. 安裝所需套件：
```bash
pip install -r requirements.txt
```

3. 設定環境變數：
建立 `.env` 檔案，並加入以下設定：
```
OPENAI_API_KEY=你的OpenAI_API金鑰
OPENAI_MODEL=gpt-4-1106-preview  # 或其他支援的模型
```

## 使用方法

1. 啟動應用程式：
```bash
streamlit run app.py
```

2. 在瀏覽器中開啟顯示的網址（預設為 http://localhost:8501）

3. 使用步驟：
   - 選擇處理選項（生成逐字稿和/或字幕檔）
   - 上傳音訊或影片檔案
   - 等待處理完成
   - 檢視結果並下載輸出檔案

## 專案結構

```
.
├── app.py                  # 主要的 Streamlit 應用程式
├── modules/
│   ├── processor.py        # 音訊/影片處理核心模組
│   ├── translator.py       # 文字翻譯模組
│   └── openai_processor.py # OpenAI 文字處理模組
├── input/                  # 輸入檔案暫存目錄
├── output/                 # 輸出檔案目錄
│   ├── transcripts/       # 逐字稿輸出
│   └── subtitles/         # 字幕檔輸出
├── model/                  # Whisper 模型存放目錄
├── temp/                   # 暫存檔案目錄
└── ffmpeg/                # FFmpeg 工具目錄（如果需要）
```

## 主要模組說明

### AudioVideoProcessor (processor.py)
- 處理音訊和影片檔案
- 使用 Whisper 模型進行語音辨識
- 生成逐字稿和字幕檔

### Translator (translator.py)
- 使用 OpenAI API 進行語言偵測和翻譯
- 支援多語言轉換為繁體中文
- 處理雙語輸出

### OpenAITextProcessor (openai_processor.py)
- 使用 OpenAI API 進行文字智能分段
- 優化文字排版和格式

## 注意事項

1. 請確保有足夠的磁碟空間用於處理檔案
2. 較大的檔案可能需要較長的處理時間
3. 需要穩定的網路連接以使用 OpenAI API
4. 使用前請確認 OpenAI API 金鑰設定正確

## 授權條款

本專案採用 Apache License 2.0 授權。

```
Copyright 2024 [clinno0616]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

詳細的授權條款內容請參閱 [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) 官方網站。

## 使用者畫面

