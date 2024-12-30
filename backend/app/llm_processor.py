from typing import Dict, Optional
import google.generativeai as genai # type: ignore
from dotenv import load_dotenv
import os
import json

load_dotenv()

class LLMProcessor:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google APIキーが設定されていません")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    async def process_company_info(self, company_data: Dict) -> Dict[str, str]:
        """企業情報を解析してLLMで加工"""
        
        # プロンプトの構築
        system_prompt = """
        以下のテキストから企業情報を抽出し、必ず以下のJSON形式で出力してください。
        テキストが長い場合でも、重要な情報を優先して抽出してください。
        他の文章は一切含めないでください。

        {
            "basic_info": {
                "company_name": "会社名を抽出してください",
                "business_description": "事業内容を抽出してください",
                "address": "所在地を抽出してください",
                "representative": "代表者名を抽出してください",
                "tel": "電話番号を抽出してください",
                "business_hours": "営業時間を抽出してください"
            },
            "analysis": {
                "summary": "企業の特徴を100文字程度で要約してください",
                "investor_analysis": "投資家向けの分析を200文字程度で記述してください",
                "job_seeker_info": "就職活動者向けの情報を200文字程度で記述してください"
            }
        }
        """

        try:
            # テキストが長い場合は分割して処理
            raw_text = company_data.get('raw_text', '')
            max_length = 30000  # Geminiの制限に応じて調整

            if len(raw_text) > max_length:
                raw_text = raw_text[:max_length] + "..."

            response = self.model.generate_content([
                {"text": system_prompt},
                {"text": f"解析対象テキスト:\n{raw_text}"}
            ])

            if response.text:
                try:
                    # 余分な文字を削除してJSONのみを抽出
                    json_text = response.text.strip()
                    if not json_text.startswith('{'):
                        json_text = json_text[json_text.find('{'):]
                    if not json_text.endswith('}'):
                        json_text = json_text[:json_text.rfind('}')+1]
                    
                    result = json.loads(json_text)
                    # raw_textを確実に含める
                    result["basic_info"]["raw_text"] = company_data.get("raw_text", "")
                    return result
                except json.JSONDecodeError as e:
                    print(f"JSON Parse Error: {str(e)}\nResponse: {response.text}")
                    return self._generate_error_response("JSONパースエラー")
            else:
                return self._generate_error_response("空の応答")

        except Exception as e:
            print(f"Error: {str(e)}")
            return self._generate_error_response(str(e))

    def _generate_error_response(self, error_message: str) -> Dict:
        """エラー時のレスポンスを生成"""
        return {
            "error": error_message,
            "basic_info": {
                "company_name": "取得できませんでした",
                "business_description": "取得できませんでした",
                "address": "取得できませんでした",
                "representative": "取得できませんでした",
                "tel": "取得できませんでした",
                "business_hours": "取得できませんでした"
            },
            "analysis": {
                "summary": "分析できませんでした",
                "investor_analysis": "分析できませんでした",
                "job_seeker_info": "分析できませんでした"
            }
        }