import whisper
import torch
import os
from pathlib import Path
from datetime import timedelta
import subprocess
import json
import numpy as np
import re
from modules.translator import Translator

class AudioVideoProcessor:
    def __init__(self):
        self.model_dir = Path("model")
        self.output_dir = Path("output")
        self.setup_directories()
        self.ffmpeg_path = self.setup_ffmpeg()
        self.model = self.load_whisper_model()
        self.translator = Translator()

    def setup_directories(self):
        """設置必要的目錄"""
        for dir_path in [self.model_dir, self.output_dir, 
                        self.output_dir / "transcripts", 
                        self.output_dir / "subtitles", 
                        Path("temp")]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def setup_ffmpeg(self):
        """設定並檢查 FFmpeg"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                 capture_output=True, 
                                 text=True)
            print("系統 FFmpeg 版本:", result.stdout.split('\n')[0])
            return 'ffmpeg'
        except FileNotFoundError:
            print("系統未安裝 FFmpeg，使用本地版本...")
            ffmpeg_dir = Path("ffmpeg/bin")
            ffmpeg_path = ffmpeg_dir / "ffmpeg.exe"
            
            if not ffmpeg_path.exists():
                print("下載 FFmpeg...")
                self.download_ffmpeg()
                
            if not ffmpeg_path.exists():
                raise Exception("FFmpeg 安裝失敗")
                
            # 將 FFmpeg 路徑加入環境變數
            os.environ["PATH"] = f"{str(ffmpeg_dir.absolute())};{os.environ['PATH']}"
            print(f"使用本地 FFmpeg: {ffmpeg_path}")
            return str(ffmpeg_path.absolute())

    def load_whisper_model(self):
        """載入 Whisper 模型"""
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"使用設備: {device}")
            model = whisper.load_model("base", 
                                     device=device, 
                                     download_root=str(self.model_dir))
            print("Whisper 模型載入成功")
            return model
        except Exception as e:
            raise Exception(f"模型載入失敗：{str(e)}")

    def extract_audio(self, video_path, output_path):
        """從影片中提取音訊"""
        try:
            # 將路徑轉換為原始字串格式，避免編碼問題
            video_path_str = str(Path(video_path).resolve())
            output_path_str = str(Path(output_path).resolve())

            command = [
            self.ffmpeg_path,
            "-i", video_path_str,
            "-vn",  # 不處理視訊
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",
            output_path_str
            ]
        
            print(f"執行指令: {' '.join(command)}")
            
            # 使用 subprocess.Popen 並設定 encoding
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='replace'
            )
        
            # 等待程序完成並獲取輸出
            stdout, stderr = process.communicate()
        
            if process.returncode != 0:
                print(f"FFmpeg 錯誤輸出: {stderr}")
                raise Exception(f"音訊提取失敗: {stderr}")
            
            if not Path(output_path).exists():
                raise FileNotFoundError(f"輸出檔案不存在: {output_path}")
            
            print(f"音訊提取成功: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"音訊提取失敗：{str(e)}")

    def transcribe_audio(self, file_path):
        """執行語音辨識並格式化文本"""
        try:
            print(f"開始處理檔案：{file_path}")
            input_path = Path(file_path).resolve()
            print(f"絕對路徑：{input_path}")

            if not input_path.exists():
                raise FileNotFoundError(f"找不到檔案：{input_path}")

            # 準備音訊檔案
            audio_path = input_path
            if input_path.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv']:
                print("正在從影片提取音訊...")
                temp_audio = Path("temp") / f"{input_path.stem}.wav"
                audio_path = self.extract_audio(input_path, temp_audio)

            print(f"開始語音辨識：{audio_path}")
            result = self.model.transcribe(
                str(audio_path),
                fp16=torch.cuda.is_available(),
                language=None,
                task='transcribe'
            )

            # 清理臨時音訊檔案
            if audio_path != input_path and Path(audio_path).exists():
                os.remove(audio_path)
                print(f"已清理臨時音訊檔案：{audio_path}")

            if not result or "text" not in result:
                raise Exception("語音辨識結果為空")

            # 檢查是否為日文
            detected_language = result.get("language", "")
            print(f"偵測到的語言: {detected_language}")
        
            original_text = result["text"]
            formatted_text = ""

            if detected_language not in ["zh", "chi", "zho", "zh-TW", "zh-CN"]:
                print(f"檢測到{detected_language}，進行翻譯...")
                # 使用 translator 進行翻譯
                from modules.translator import Translator
                translator = Translator()
                
                # 分段處理文本
                original_paragraphs = self.format_transcript(original_text).split('\n\n')
                formatted_paragraphs = []
                
                for paragraph in original_paragraphs:
                    if paragraph.strip():
                        # 翻譯每個段落
                        translation_result = translator.translate_to_lang(paragraph.strip(),detected_language)
                        formatted_paragraphs.append(translation_result['original'])
                        formatted_paragraphs.append(translation_result['translated'])
                        formatted_paragraphs.append('')  # 添加空行分隔段落
                
                formatted_text = '\n'.join(formatted_paragraphs).strip()
            else:
                # 使用 translator 進行翻譯
                from modules.translator import Translator
                translator = Translator()
                # 中文則使用原本的格式化方式
                translated_text = translator.translate_to_chinese(original_text)
                formatted_text = self.format_transcript(translated_text)
            

            # 保存逐字稿到 output/transcripts 目錄
            transcript_filename = f"{input_path.stem}_transcript.txt"
            transcript_path = self.output_dir / "transcripts" / transcript_filename
            
            try:
                with open(transcript_path, "w", encoding="utf-8") as f:
                    f.write(formatted_text)
                print(f"逐字稿已保存到：{transcript_path}")
            except Exception as e:
                print(f"保存逐字稿時發生錯誤：{str(e)}")
            
            return formatted_text

        except Exception as e:
            import traceback
            print(f"錯誤堆疊：\n{traceback.format_exc()}")
            raise Exception(f"語音辨識失敗：{str(e)}")
            
    def generate_subtitles(self, file_path, output_format="srt"):
        """生成字幕檔"""
        try:
            print(f"開始處理檔案：{file_path}")
            input_path = Path(file_path).resolve()

            # 準備音訊檔案
            audio_path = input_path
            if input_path.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv']:
                print("正在從影片提取音訊...")
                temp_audio = Path("temp") / f"{input_path.stem}.wav"
                audio_path = self.extract_audio(input_path, temp_audio)

            print("執行語音辨識...")
            result = self.model.transcribe(
                str(audio_path),
                fp16=torch.cuda.is_available(),
                language=None,
                task='transcribe'
            )

            # 檢查偵測到的語言
            detected_language = result.get("language", "")
            print(f"偵測到的語言: {detected_language}")

            # 如果不是中文，就翻譯
            if detected_language not in ["zh", "chi", "zho", "zh-TW", "zh-CN"]:
                print("非中文字幕，開始翻譯...")
                from modules.translator import Translator
                translator = Translator()
                
                # 翻譯每個段落
                for segment in result["segments"]:
                    original_text = segment["text"].strip()
                    translated_text = translator.translate_to_chinese(original_text)
                    segment["text"] = translated_text
                    # 保存原文到新的鍵
                    segment["original_text"] = original_text

            # 生成字幕檔
            subtitle_path = self.output_dir / "subtitles" / f"{input_path.stem}.{output_format}"
            bilingual_subtitle_path = self.output_dir / "subtitles" / f"{input_path.stem}_bilingual.{output_format}"
            
            # 生成單語字幕（只有中文）
            print("生成中文字幕...")
            with open(subtitle_path, "w", encoding="utf-8") as f:
                if output_format == "vtt":
                    f.write("WEBVTT\n\n")
                    
                for i, segment in enumerate(result["segments"], start=1):
                    start = str(timedelta(seconds=int(segment["start"])))
                    end = str(timedelta(seconds=int(segment["end"])))
                    text = segment["text"].strip()
                    
                    if output_format == "srt":
                        f.write(f"{i}\n")
                        f.write(f"{start} --> {end}\n")
                        f.write(f"{text}\n\n")
                    else:  # vtt
                        f.write(f"{start} --> {end}\n")
                        f.write(f"{text}\n\n")

            # 如果有原文，生成雙語字幕
            if any("original_text" in segment for segment in result["segments"]):
                print("生成雙語字幕...")
                with open(bilingual_subtitle_path, "w", encoding="utf-8") as f:
                    if output_format == "vtt":
                        f.write("WEBVTT\n\n")
                    
                    for i, segment in enumerate(result["segments"], start=1):
                        start = str(timedelta(seconds=int(segment["start"])))
                        end = str(timedelta(seconds=int(segment["end"])))
                        text = segment["text"].strip()
                        original = segment.get("original_text", "").strip()
                        
                        if output_format == "srt":
                            f.write(f"{i}\n")
                            f.write(f"{start} --> {end}\n")
                            if original:
                                f.write(f"{original}\n{text}\n\n")
                            else:
                                f.write(f"{text}\n\n")
                        else:  # vtt
                            f.write(f"{start} --> {end}\n")
                            if original:
                                f.write(f"{original}\n{text}\n\n")
                            else:
                                f.write(f"{text}\n\n")

            # 清理臨時音訊檔案
            if audio_path != input_path and Path(audio_path).exists():
                os.remove(audio_path)
                print(f"已清理臨時音訊檔案：{audio_path}")

            return str(subtitle_path), str(bilingual_subtitle_path) if Path(bilingual_subtitle_path).exists() else None

        except Exception as e:
            import traceback
            print(f"錯誤堆疊：\n{traceback.format_exc()}")
            raise Exception(f"字幕生成失敗：{str(e)}")

    def download_ffmpeg(self):
        """下載並解壓 FFmpeg"""
        import requests
        import zipfile
        import shutil
        
        ffmpeg_dir = Path("ffmpeg/bin")
        ffmpeg_dir.mkdir(parents=True, exist_ok=True)
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # 使用更可靠的下載源
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n6.0-latest-win64-gpl-6.0.zip"
            zip_path = temp_dir / "ffmpeg.zip"
            
            print("下載 FFmpeg...")
            response = requests.get(ffmpeg_url)
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            print("解壓 FFmpeg...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 移動必要的檔案
            extracted_dir = next(temp_dir.glob('ffmpeg-*'))
            bin_dir = extracted_dir / 'bin'
            
            for file in bin_dir.glob('*.exe'):
                shutil.copy2(file, ffmpeg_dir)
            
            print("FFmpeg 安裝完成")
            
        except Exception as e:
            print(f"FFmpeg 下載失敗：{str(e)}")
            raise
        finally:
            # 清理臨時檔案
            if 'zip_path' in locals() and zip_path.exists():
                zip_path.unlink()
            if 'extracted_dir' in locals() and extracted_dir.exists():
                shutil.rmtree(extracted_dir, ignore_errors=True)

    def format_transcript(self, text):
        """格式化逐字稿，添加標點符號和段落分隔"""
        if not text:
            return ""
            
        # 1. 基本清理
        text = text.strip()
        
        # 2. 分句和加入標點符號
        # 根據語音停頓和語意添加句號
        sentences = re.split(r'(?<=[。！？\!?])|(?<=[\w\d])\s+(?=[A-Z])', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 為沒有結束標點的句子添加句號
        formatted_sentences = []
        for sentence in sentences:
            if not sentence[-1] in '。！？!?.':
                sentence += '。'
            formatted_sentences.append(sentence)
        
        # 3. 段落處理
        # 根據句子數量和長度自動分段
        paragraphs = []
        current_paragraph = []
        
        for sentence in formatted_sentences:
            current_paragraph.append(sentence)
            
            # 當前段落超過3句話或字數超過100，就分段
            current_text = ''.join(current_paragraph)
            if len(current_paragraph) >= 3 or len(current_text) >= 100:
                paragraphs.append(''.join(current_paragraph))
                current_paragraph = []
        
        # 處理剩餘的句子
        if current_paragraph:
            paragraphs.append(''.join(current_paragraph))
        
        # 4. 合併段落，使用兩個換行符分隔
        formatted_text = '\n\n'.join(paragraphs)
        
        return formatted_text                
