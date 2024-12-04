from openai import OpenAI
from dotenv import load_dotenv
import time
import opencc
import os
from pathlib import Path

class Translator:
    def __init__(self):
        # 載入環境變數
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_model = os.getenv('OPENAI_MODEL')
        if not self.api_key:
            raise ValueError("未設定 OPENAI_API_KEY 環境變數")
        
        # 初始化 OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        self.max_retries = 3
        self.delay_between_retries = 1  # 秒
        
        try:
            import opencc
            self.converter = opencc.OpenCC('s2twp')  # 不需要加 .json
        except ImportError:
            print("無法載入 opencc，將使用替代方案")
            self.converter = None
            
    def detect_language(self, text):
        """使用 OpenAI 偵測文字語言"""
        try:
            prompt = f"""
            請判斷以下文字的語言，只需要返回語言代碼，不需要其他解釋。
            支援的語言代碼：
            zh-tw: 繁體中文
            zh-cn: 簡體中文
            en: 英文
            ja: 日文
            ko: 韓文
            其他語言請返回 ISO 639-1 代碼。

            文字內容:
            {text}
            """
            
            response = self.client.chat.completions.create(
                model=self.api_model,
                messages=[
                    {"role": "system", "content": "你是一個語言偵測專家，專門判斷文字的語言類型。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            return response.choices[0].message.content.strip().lower()
            
        except Exception as e:
            print(f"語言偵測失敗：{str(e)}")
            return None
            
    def translate_to_chinese(self, text):
        """將文字翻譯成繁體中文"""
        if not text:
            print("警告: 收到空的文字內容")
            return ""
            
        print(f"開始翻譯文字，長度：{len(text)}")
        retries = 0
        
        while retries < self.max_retries:
            try:
                # 偵測語言
                detected_lang = self.detect_language(text)
                print(f"偵測到的語言：{detected_lang}")
                
                # 如果已經是繁體中文，直接返回
                if detected_lang == 'zh-tw':
                    print("文字已經是繁體中文")
                    return text
                
                # 如果是簡體中文，直接轉換
                if detected_lang in ['zh-cn', 'zh']:
                    print("將簡體中文轉換為繁體中文")
                    return self.converter.convert(text) if self.converter else text
                
                # 其他語言使用 OpenAI 翻譯為中文
                prompt = f"""
                請將以下文字翻譯成流暢的繁體中文：

                {text}

                注意事項：
                1. 請保持原文的語氣和風格
                2. 使用繁體中文
                3. 只返回翻譯結果，不要加入任何解釋或標記
                """
                
                response = self.client.chat.completions.create(
                    model=self.api_model,
                    messages=[
                        {"role": "system", "content": "你是一個專業的翻譯專家，專門將各種語言翻譯成流暢的繁體中文。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=16384
                )
                
                translated = response.choices[0].message.content.strip()
                
                # 使用 opencc 確保是繁體中文
                result = self.converter.convert(translated) if self.converter else translated
                print("翻譯完成")
                return result
                    
            except Exception as e:
                print(f"翻譯嘗試 {retries + 1} 失敗：{str(e)}")
                retries += 1
                if retries == self.max_retries:
                    raise Exception(f"翻譯失敗：{str(e)}")
                time.sleep(self.delay_between_retries)
    
    def translate_to_lang(self, text, lang):
        """處理文本並翻譯成中文，返回原文和中文翻譯的對照"""
        if not text:
            print("警告: 收到空的文字內容")
            return {"original": "", "translated": ""}

        retries = 0
        while retries < self.max_retries:
            try:
                # 保存原文
                original_text = text.strip()
                
                # 翻譯成中文
                prompt = f"""
                請將以下 {lang} 文字翻譯成流暢的繁體中文：

                {text}

                注意事項：
                1. 請保持原文的語氣和風格
                2. 使用繁體中文
                3. 保留原文文字，一行顯示原文，另一行為翻譯結果，不要加入任何解釋或標記
                """
                
                response = self.client.chat.completions.create(
                    model=self.api_model,
                    messages=[
                        {"role": "system", "content": "你是一個專業的翻譯專家，專門進行高品質的翻譯工作。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=16384
                )
                
                translated = response.choices[0].message.content.strip()
                
                # 確保結果為繁體中文
                result = self.converter.convert(translated) if self.converter else translated

                return {
                    'original': original_text,
                    'translated': result
                }

            except Exception as e:
                print(f"翻譯嘗試 {retries + 1} 失敗：{str(e)}")
                retries += 1
                if retries == self.max_retries:
                    raise Exception(f"翻譯失敗：{str(e)}")
                time.sleep(self.delay_between_retries)
                
        return {"original": text, "translated": text}  # 如果全部都失敗，返回原文
