import os
from openai import OpenAI
from dotenv import load_dotenv
import re

class OpenAITextProcessor:
    def __init__(self):
        # 載入環境變數
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_model = os.getenv('OPENAI_MODEL')
        if not self.api_key:
            raise ValueError("未設定 OPENAI_API_KEY 環境變數")
        
        # 初始化 OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
    def get_semantic_segments(self, text):
        """使用 OpenAI 進行中文語意分析和分段"""
        try:
            # 準備 prompt
            prompt = f"""
            請將以下文字進行語意分析並分段。每個段落應該具有連貫的語意脈絡。
            請只返回分段後的文字，不要加入任何解釋或評論。
            確保每個段落都以適當的標點符號結尾。

            文字內容:
            {text}
            """
            
            # 調用 OpenAI API
            response = self.client.chat.completions.create(
                model=self.api_model,
                messages=[
                    {"role": "system", "content": "你是一個專業的文字編輯,擅長進行文字的語意分析和分段處理。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 降低隨機性
                max_tokens=16384
            )
            
            # 取得回應內容
            segmented_text = response.choices[0].message.content.strip()
            
            # 將回應內容分割成段落
            paragraphs = [p.strip() for p in segmented_text.split('\n') if p.strip()]
            
            return paragraphs
            
        except Exception as e:
            print(f"OpenAI API 呼叫失敗：{str(e)}")
            return None

    def process_text(self, text):
        """處理文本,返回格式化後的文本"""
        if not text:
            return ""
            
        try:
            # 使用 OpenAI 進行語意分段
            paragraphs = self.get_semantic_segments(text)
            
            if not paragraphs:
                # 如果 API 處理失敗,使用基本的分段方法
                return self.basic_segment(text)
            
            # 後處理：確保每個段落都有適當的標點符號
            processed_paragraphs = []
            for paragraph in paragraphs:
                # 移除段落開頭的編號(如果有)
                paragraph = re.sub(r'^\d+\.\s*', '', paragraph)
                
                # 確保段落以適當的標點符號結束
                if not paragraph[-1] in '。！？':
                    paragraph += '。'
                processed_paragraphs.append(paragraph)
            
            # 合併段落,使用兩個換行符分隔
            formatted_text = '\n\n'.join(processed_paragraphs)
            return formatted_text
            
        except Exception as e:
            print(f"文本處理失敗：{str(e)}")
            return self.basic_segment(text)
            
    def basic_segment(self, text):
        """基本的中文文本分段方法,作為備用"""
        # 移除多餘的空白
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 使用標點符號分割句子
        sentence_pattern = r'[。！？!?]+\s*|[.]+\s+'
        sentences = re.split(sentence_pattern, text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 為句子添加適當的標點符號
        formatted_sentences = []
        for sentence in sentences:
            if not sentence[-1] in '。！？':
                sentence += '。'
            formatted_sentences.append(sentence)
        
        # 根據句子長度和數量自動分段
        paragraphs = []
        current_paragraph = []
        current_length = 0
        
        for sentence in formatted_sentences:
            current_paragraph.append(sentence)
            current_length += len(sentence)
            
            # 當段落累積3句話或超過150個字就分段
            if len(current_paragraph) >= 3 or current_length >= 150:
                paragraphs.append(''.join(current_paragraph))
                current_paragraph = []
                current_length = 0
        
        # 處理剩餘的句子
        if current_paragraph:
            paragraphs.append(''.join(current_paragraph))
        
        return '\n\n'.join(paragraphs)