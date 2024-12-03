from googletrans import Translator as GoogleTranslator
import time
import opencc
import os
from pathlib import Path

class Translator:
    def __init__(self):
        self.translator = None
        self.max_retries = 3
        self.delay_between_retries = 1  # 秒
        try:
            import opencc
            self.converter = opencc.OpenCC('s2twp')  # 不需要加 .json
        except ImportError:
            print("無法載入 opencc，將使用替代方案")
            self.converter = None  # 使用繁體中文優先的轉換
        
    def ensure_translator(self):
        """確保翻譯器已初始化"""
        if self.translator is None:
            self.translator = GoogleTranslator()
        
    def translate_to_chinese(self, text):
        """將文字翻譯成繁體中文"""
        if not text:
            print("警告: 收到空的文字內容")
            return ""
            
        #print(f"開始翻譯文字，長度：{len(text)}")
        retries = 0
        while retries < self.max_retries:
            try:
                self.ensure_translator()
                
                # 先偵測語言
                detected = self.translator.detect(text)
                #print(f"偵測到的語言：{detected.lang}")
                
                # 如果已經是繁體中文，直接返回
                if detected.lang == 'zh-tw':
                    print("文字已經是繁體中文")
                    return text
                
                # 如果是簡體中文，直接轉換
                if detected.lang in ['zh-cn', 'zh']:
                    print("將簡體中文轉換為繁體中文")
                    return self.converter.convert(text)
                
                # 其他語言翻譯為中文
                translated = self.translator.translate(text, dest='zh-tw')
                if not translated or not translated.text:
                    raise Exception("翻譯結果為空")
                
                # 確保結果為繁體中文
                result = self.converter.convert(translated.text)
                #print("翻譯完成")
                return result
                    
            except Exception as e:
                print(f"翻譯嘗試 {retries + 1} 失敗：{str(e)}")
                retries += 1
                if retries == self.max_retries:
                    raise Exception(f"翻譯失敗：{str(e)}")
                time.sleep(self.delay_between_retries)
                self.translator = None
    
   
    def translate_to_lang(self, text, lang):
        """處理英文文本並翻譯成中文，返回英文和中文翻譯的對照"""
        if not text:
            print("警告: 收到空的文字內容")
            return ""

        retries = 0
        while retries < self.max_retries:
            try:
                self.ensure_translator()

                # 翻譯為中文
                translated = self.translator.translate(text, src= lang, dest='zh-tw')
                if not translated or not translated.text:
                    raise Exception("翻譯結果為空")

                # 確保結果為繁體中文
                result = self.converter.convert(translated.text)

                # 返回原文和翻譯的對照格式
                return {
                    'original': text,
                    'translated': result
                }

            except Exception as e:
                print(f"翻譯嘗試 {retries + 1} 失敗：{str(e)}")
                retries += 1
                if retries == self.max_retries:
                    raise Exception(f"翻譯失敗：{str(e)}")
                time.sleep(self.delay_between_retries)
                self.translator = None