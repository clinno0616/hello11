import streamlit as st
import os
from pathlib import Path
from modules.processor import AudioVideoProcessor
from modules.player import VideoPlayer
from modules.translator import Translator

# 設定頁面配置
st.set_page_config(
    page_title="音訊/影片轉文字系統",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化目錄
input_dir = Path("input")
output_dir = Path("output")
model_dir = Path("model")
temp_dir = Path("temp")
ffmpeg_dir = Path("ffmpeg/bin")

# 創建必要的目錄
for directory in [input_dir, output_dir, model_dir, temp_dir, ffmpeg_dir]:
    directory.mkdir(parents=True, exist_ok=True)

# 創建輸出子目錄
(output_dir / "transcripts").mkdir(exist_ok=True)
(output_dir / "subtitles").mkdir(exist_ok=True)

def initialize_session_state():
    """初始化 session state"""
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None
    if 'transcript_path' not in st.session_state:
        st.session_state.transcript_path = None
    if 'subtitle_path' not in st.session_state:
        st.session_state.subtitle_path = None
    if 'bilingual_subtitle_path' not in st.session_state:
        st.session_state.bilingual_subtitle_path = None
    if 'input_path' not in st.session_state:
        st.session_state.input_path = None
    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0

def process_file(uploaded_file, progress_bar, status_text):
    """處理上傳的檔案"""
    try:
        # 初始化處理器
        processor = AudioVideoProcessor()
        translator = Translator()
        
        # 將上傳的檔案保存到 input 目錄
        input_path = Path("input") / uploaded_file.name
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if not input_path.exists():
            raise Exception(f"檔案保存失敗：{input_path}")
            
        st.session_state.input_path = input_path
        print(f"檔案已保存到：{input_path}")
        
        # 處理檔案
        status_text.text("正在處理檔案...")
        progress_bar.progress(25)
        
        # 執行語音辨識
        print("開始執行語音辨識...")
        transcription = processor.transcribe_audio(str(input_path))
        print("語音辨識完成")
        progress_bar.progress(50)
        
        # 翻譯為中文
        status_text.text("正在翻譯...")
        translated_text = translator.translate_to_chinese(transcription)
        st.session_state.transcript = translated_text
        progress_bar.progress(75)
        
        # 生成字幕檔
        if uploaded_file.type.startswith('video'):
            status_text.text("正在生成字幕...")
            subtitle_path, bilingual_subtitle_path = processor.generate_subtitles(str(input_path))
            st.session_state.subtitle_path = subtitle_path
            st.session_state.bilingual_subtitle_path = bilingual_subtitle_path
            progress_bar.progress(90)
        
        st.session_state.processed = True
        progress_bar.progress(100)
        status_text.text("處理完成！")
        
        return True
        
    except Exception as e:
        st.error(f"處理過程中發生錯誤：{str(e)}")
        return False

def display_results():
    """顯示處理結果和下載按鈕"""
    if not st.session_state.processed:
        return
        
    # 顯示影片播放器（如果有）
    #if st.session_state.subtitle_path and st.session_state.input_path.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv']:
    #    player = VideoPlayer()
    #    player.display_video(str(st.session_state.input_path), st.session_state.subtitle_path)
    
    # 顯示文字結果
    st.markdown("### 轉換結果")
    # 使用 markdown 來正確顯示換行
    formatted_transcript = st.session_state.transcript.replace('\n', '  \n')
    st.markdown(formatted_transcript)
    
    # 為了編輯和複製方便，也提供一個可展開的文本區域
    with st.expander("展開文本編輯區"):
        edited_transcript = st.text_area(
            "您可以在這裡編輯文本",
            st.session_state.transcript,
            height=300
        )
        
        # 如果文本被編輯，更新 session state
        if edited_transcript != st.session_state.transcript:
            st.session_state.transcript = edited_transcript
    
    # 建立下載按鈕
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="下載逐字稿",
            data=st.session_state.transcript,
            file_name=f"{st.session_state.input_path.stem}_transcript.txt",
            mime="text/plain"
        )
    
    # 如果有字幕檔，提供下載
    if st.session_state.subtitle_path and Path(st.session_state.subtitle_path).exists():
        with open(st.session_state.subtitle_path, "r", encoding="utf-8") as f:
            subtitle_content = f.read()
        with col2:
            st.download_button(
                label="下載中文字幕檔",
                data=subtitle_content,
                file_name=f"{st.session_state.input_path.stem}_subtitle.srt",
                mime="text/plain"
            )
    
    # 如果有雙語字幕檔，提供下載
    if st.session_state.bilingual_subtitle_path and Path(st.session_state.bilingual_subtitle_path).exists():
        with open(st.session_state.bilingual_subtitle_path, "r", encoding="utf-8") as f:
            bilingual_subtitle_content = f.read()
        with col3:
            st.download_button(
                label="下載雙語字幕檔",
                data=bilingual_subtitle_content,
                file_name=f"{st.session_state.input_path.stem}_subtitle_bilingual.srt",
                mime="text/plain"
            )

def main():
    st.title("音訊/影片轉文字系統")
    initialize_session_state()
  
    # 重新開始按鈕
    #if st.session_state.processed:
    if st.button("重新開始(先按『重新開始』，再重新上傳檔案，才可以開始另外一個轉換任務!)"):
        # 清理 session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        # 清理檔案
        for path in [temp_dir, input_dir]:
            for file in path.glob("*"):
                try:
                    os.remove(file)
                except Exception as e:
                    print(f"清理檔案失敗：{str(e)}")
        initialize_session_state()
        st.rerun()

    # 檔案上傳
    uploaded_file = st.file_uploader(
        "上傳音訊或影片檔案(僅限一個檔案)",
        type=['mp3', 'wma', 'wav', 'm4a', 'mp4', 'mov', 'avi', 'mkv'],
        key="file_uploader"
    )

    # 處理上傳的檔案
    if uploaded_file is not None:
        # 如果上傳了新檔案且與當前處理的檔案不同
        if st.session_state.current_file != uploaded_file.name:
            st.session_state.processed = False
            st.session_state.current_file = uploaded_file.name
            
        # 如果檔案未處理
        if not st.session_state.processed:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            if process_file(uploaded_file, progress_bar, status_text):
                st.session_state.processed = True
                display_results()
        
        # 如果檔案已處理，直接顯示結果
        elif st.session_state.processed:
            display_results()

if __name__ == "__main__":
    main()