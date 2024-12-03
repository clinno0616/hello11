# 音訊/影片轉文字系統 (Audio/Video Transcription System)

這是一個基於 Streamlit 開發的音訊和影片轉文字系統，能夠將音訊或影片檔案轉換成文字稿，並支援多語言翻譯與字幕生成功能。

## 功能特點

- 支援多種音訊和影片格式（mp3、wma、wav、m4a、mp4、mov、avi、mkv）
- 自動語言偵測與翻譯
- 生成中文/雙語字幕檔（SRT 格式）
- 支援逐字稿編輯與下載
- 使用者友善的網頁介面

## 系統需求

- Python 3.7+
- FFmpeg（如果系統未安裝，程式會自動下載）
- CUDA 支援（選配，可加速語音辨識處理）

## 安裝步驟

1. 克隆專案存儲庫：
```bash
git clone https://github.com/clinno0616/hello11.git
cd hello11
```

2. 安裝所需套件：
```bash
pip install -r requirements.txt
```

## 主要依賴套件

- streamlit：網頁應用框架
- whisper：OpenAI 的語音辨識模型
- googletrans：Google 翻譯 API
- opencc：中文簡繁轉換
- torch：PyTorch（用於 Whisper 模型）

## 使用方法

1. 啟動應用程式：
```bash
streamlit run app.py
```

2. 在瀏覽器中開啟顯示的網址（預設為 http://localhost:8501）

3. 使用步驟：
   - 點擊「上傳音訊或影片檔案」選擇要處理的檔案
   - 等待系統處理（包含語音辨識、翻譯等步驟）
   - 在處理完成後，可以：
     - 檢視轉換結果
     - 編輯文字內容
     - 下載逐字稿和字幕檔

## 專案結構

```
.
├── app.py                  # 主程式入口
├── modules/
│   ├── processor.py       # 音訊/影片處理模組
│   └── translator.py      # 翻譯處理模組
├── input/                 # 輸入檔案暫存目錄
├── output/               # 輸出檔案目錄
│   ├── transcripts/     # 逐字稿輸出目錄
│   └── subtitles/       # 字幕檔輸出目錄
├── model/                # Whisper 模型目錄
├── temp/                # 暫存檔案目錄
└── ffmpeg/              # FFmpeg 執行檔目錄
```

## 注意事項

- 檔案處理時間依檔案大小和系統效能而定
- 建議使用具有 CUDA 支援的系統以提升處理效率
- 翻譯功能需要網路連線

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
